"""
LPU GoCart - Seat Locking & Booking REST Router
Atomic reservation and ticketing API.
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import (
    Booking, SeatLock, CartSeat, Cart, Trip, RouteStop, User, QRTicket, LuggageBooking
)
from app.schemas.booking import (
    SeatLockRequest, SeatLockResponse, BookingCreateRequest, BookingResponse, TicketResponse
)
from app.services.seat_lock_service import acquire_seat_lock, release_seat_lock
from app.services.booking_service import create_pending_booking
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings & Seat Locking"])

def ensure_active_trip(db: Session, cart_id: str, trip_id: Optional[str] = None) -> Trip:
    """Find active or scheduled trip for a cart, or create one automatically."""
    if trip_id:
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if trip:
            return trip

    trip = db.query(Trip).filter(
        Trip.cart_id == cart_id,
        Trip.status.in_(["SCHEDULED", "ACTIVE"])
    ).first()

    if not trip:
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found.")
        
        # Determine driver and route
        driver_id = cart.driver_id
        if not driver_id:
            # Fallback to default driver
            driver = db.query(User).filter(User.role == "DRIVER").first()
            driver_id = driver.id if driver else None

        route_id = cart.current_route_id
        if not route_id:
            from app.database.models import Route
            route = db.query(Route).first()
            route_id = route.id if route else None

        if not driver_id or not route_id:
            raise HTTPException(status_code=400, detail="Cannot create trip: Driver or route not assigned.")

        trip = Trip(
            cart_id=cart.id,
            driver_id=driver_id,
            route_id=route_id,
            status="SCHEDULED"
        )
        db.add(trip)
        db.commit()
        db.refresh(trip)

    return trip

@router.post("/lock-seat", response_model=SeatLockResponse)
def lock_cart_seat(
    req: SeatLockRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atomic Seat Reservation Lock:
    Temporarily holds a seat for 5 minutes during checkout.
    """
    seat = db.query(CartSeat).filter(CartSeat.id == req.seat_id).first()
    if not seat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found.")

    trip = ensure_active_trip(db, req.cart_id, req.trip_id)

    success, lock, msg = acquire_seat_lock(
        db=db,
        trip_id=trip.id,
        seat_id=req.seat_id,
        user_id=current_user.id
    )

    if not success or not lock:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

    from app.services.seat_lock_service import to_utc
    now = datetime.now(timezone.utc)
    exp = to_utc(lock.expires_at) or now
    remaining_secs = max(0, int((exp - now).total_seconds()))

    return SeatLockResponse(
        lock_id=lock.id,
        trip_id=lock.trip_id,
        seat_id=lock.seat_id,
        seat_number=seat.seat_number,
        seat_label=seat.seat_label,
        locked_at=lock.locked_at,
        expires_at=lock.expires_at,
        remaining_seconds=remaining_secs
    )

@router.post("/create-pending", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    req: BookingCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a pending booking from a validated seat lock or full cart selection."""
    trip = ensure_active_trip(db, req.cart_id, req.trip_id)

    success, booking, msg = create_pending_booking(
        db=db,
        user_id=current_user.id,
        lock_id=req.lock_id,
        trip_id=trip.id,
        cart_id=req.cart_id,
        pickup_stop_id=req.pickup_stop_id,
        drop_stop_id=req.drop_stop_id,
        seat_id=req.seat_id,
        booking_type=req.booking_type,
        total_amount=req.fare_amount + req.luggage_fee,
        small_bags=req.small_bags,
        medium_bags=req.medium_bags,
        large_bags=req.large_bags,
        luggage_fee=req.luggage_fee
    )

    if not success or not booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    seat = db.query(CartSeat).filter(CartSeat.id == booking.seat_id).first() if booking.seat_id else None
    cart = db.query(Cart).filter(Cart.id == booking.cart_id).first()
    pickup = db.query(RouteStop).filter(RouteStop.id == booking.pickup_stop_id).first()
    drop = db.query(RouteStop).filter(RouteStop.id == booking.drop_stop_id).first()

    return BookingResponse(
        id=booking.id,
        booking_code=booking.booking_code,
        user_id=booking.user_id,
        trip_id=booking.trip_id,
        cart_id=cart.id if cart else "",
        cart_number=cart.cart_number if cart else "N/A",
        booking_type=booking.booking_type,
        seat_number=seat.seat_number if seat else None,
        seat_label=seat.seat_label if seat else ("Full Cart" if booking.booking_type == "FULL_CART" else "General"),
        pickup_stop_name=pickup.name if pickup else "Pickup",
        drop_stop_name=drop.name if drop else "Drop",
        fare_amount=booking.total_amount,
        status=booking.status,
        created_at=booking.created_at,
        qr_token=None
    )

@router.get("/my", response_model=List[BookingResponse])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List bookings placed by the authenticated passenger."""
    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.id
    ).order_by(Booking.created_at.desc()).all()

    result = []
    for b in bookings:
        seat = b.seat
        cart = db.query(Cart).filter(Cart.id == b.cart_id).first()
        qr = b.qr_ticket.qr_token if b.qr_ticket else None
        result.append(BookingResponse(
            id=b.id,
            booking_code=b.booking_code,
            user_id=b.user_id,
            trip_id=b.trip_id,
            cart_id=cart.id if cart else "",
            cart_number=cart.cart_number if cart else "N/A",
            booking_type=b.booking_type,
            seat_number=seat.seat_number if seat else None,
            seat_label=seat.seat_label if seat else ("Full Cart" if b.booking_type == "FULL_CART" else "General"),
            pickup_stop_name=b.pickup_stop.name if b.pickup_stop else "Pickup",
            drop_stop_name=b.drop_stop.name if b.drop_stop else "Drop",
            fare_amount=b.total_amount,
            status=b.status,
            created_at=b.created_at,
            qr_token=qr
        ))
    return result

@router.get("/{booking_id}/ticket", response_model=TicketResponse)
def get_boarding_ticket(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve digital QR boarding ticket for a confirmed reservation."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

    if booking.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if not booking.qr_ticket:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No QR ticket issued. Booking status is {booking.status}."
        )

    seat = booking.seat
    cart = db.query(Cart).filter(Cart.id == booking.cart_id).first()

    return TicketResponse(
        booking_id=booking.id,
        booking_code=booking.booking_code,
        qr_token=booking.qr_ticket.qr_token,
        passenger_name=booking.user.full_name if booking.user else current_user.full_name,
        cart_number=cart.cart_number if cart else "N/A",
        seat_label=seat.seat_label if seat else ("Full Cart" if booking.booking_type == "FULL_CART" else "General"),
        booking_type=booking.booking_type,
        pickup_stop=booking.pickup_stop.name if booking.pickup_stop else "Pickup",
        drop_stop=booking.drop_stop.name if booking.drop_stop else "Drop",
        fare=booking.total_amount,
        status=booking.status,
        created_at=booking.created_at
    )
