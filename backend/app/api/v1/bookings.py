"""
LPU GoCart - Seat Locking & Booking REST Router
Atomic reservation and ticketing API.
"""

from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models.models import (
    Booking, SeatLock, CartSeat, Cart, Trip, RouteStop, Profile, QRTicket
)
from app.schemas.booking import (
    SeatLockRequest, SeatLockResponse, BookingCreateRequest, BookingResponse, TicketResponse
)
from app.services.seat_lock_service import acquire_seat_lock, release_seat_lock
from app.services.booking_service import create_pending_booking
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings & Seat Locking"])

@router.post("/lock-seat", response_model=SeatLockResponse)
def lock_cart_seat(
    req: SeatLockRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atomic Seat Reservation Lock:
    Temporarily holds a seat for 5 minutes during checkout.
    Guarantees no two students can hold or book the same seat simultaneously.
    """
    seat = db.query(CartSeat).filter(CartSeat.id == req.seat_id).first()
    if not seat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found.")

    # Find or auto-create scheduled active trip for this cart if none exists
    trip = db.query(Trip).filter(Trip.id == req.trip_id).first()
    if not trip:
        # Lookup active trip on cart
        trip = db.query(Trip).filter(
            Trip.cart_id == req.cart_id,
            Trip.status.in_(["SCHEDULED", "IN_TRANSIT"])
        ).first()

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active trip found for this cart. Cart might be offline or charging."
        )

    success, lock, msg = acquire_seat_lock(
        db=db,
        trip_id=trip.id,
        seat_id=req.seat_id,
        student_id=current_user.id
    )

    if not success or not lock:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)

    now = datetime.now(timezone.utc)
    remaining_secs = max(0, int((lock.expires_at - now).total_seconds()))

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
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a pending booking from a validated seat lock."""
    success, booking, msg = create_pending_booking(
        db=db,
        student_id=current_user.id,
        lock_id=req.lock_id,
        trip_id=req.trip_id,
        seat_id=req.seat_id,
        pickup_stop_id=req.pickup_stop_id,
        drop_stop_id=req.drop_stop_id,
        fare_amount=req.fare_amount
    )

    if not success or not booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    seat = db.query(CartSeat).filter(CartSeat.id == booking.seat_id).first()
    cart = seat.cart if seat else None
    pickup = db.query(RouteStop).filter(RouteStop.id == booking.pickup_stop_id).first()
    drop = db.query(RouteStop).filter(RouteStop.id == booking.drop_stop_id).first()

    return BookingResponse(
        id=booking.id,
        booking_code=booking.booking_code,
        student_id=booking.student_id,
        trip_id=booking.trip_id,
        cart_id=cart.id if cart else "",
        cart_number=cart.cart_number if cart else "N/A",
        seat_number=seat.seat_number if seat else 0,
        seat_label=seat.seat_label if seat else "S",
        pickup_stop_name=pickup.name if pickup else "Pickup",
        drop_stop_name=drop.name if drop else "Drop",
        fare_amount=booking.fare_amount,
        status=booking.status,
        created_at=booking.created_at,
        qr_token=None
    )

@router.get("/my", response_model=List[BookingResponse])
def get_my_bookings(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List bookings placed by the authenticated student."""
    bookings = db.query(Booking).filter(
        Booking.student_id == current_user.id
    ).order_by(Booking.created_at.desc()).all()

    result = []
    for b in bookings:
        seat = b.seat
        cart = seat.cart if seat else None
        qr = b.qr_ticket.qr_token if b.qr_ticket else None
        result.append(BookingResponse(
            id=b.id,
            booking_code=b.booking_code,
            student_id=b.student_id,
            trip_id=b.trip_id,
            cart_id=cart.id if cart else "",
            cart_number=cart.cart_number if cart else "N/A",
            seat_number=seat.seat_number if seat else 0,
            seat_label=seat.seat_label if seat else "S",
            pickup_stop_name=b.pickup_stop.name if b.pickup_stop else "Pickup",
            drop_stop_name=b.drop_stop.name if b.drop_stop else "Drop",
            fare_amount=b.fare_amount,
            status=b.status,
            created_at=b.created_at,
            qr_token=qr
        ))
    return result

@router.get("/{booking_id}/ticket", response_model=TicketResponse)
def get_boarding_ticket(
    booking_id: str,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve digital QR boarding ticket for a confirmed reservation."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

    if booking.student_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if not booking.qr_ticket:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No QR ticket issued. Booking status is {booking.status}."
        )

    seat = booking.seat
    cart = seat.cart if seat else None

    return TicketResponse(
        booking_id=booking.id,
        booking_code=booking.booking_code,
        qr_token=booking.qr_ticket.qr_token,
        student_name=current_user.full_name,
        cart_number=cart.cart_number if cart else "N/A",
        seat_label=seat.seat_label if seat else "S",
        pickup_stop=booking.pickup_stop.name if booking.pickup_stop else "Pickup",
        drop_stop=booking.drop_stop.name if booking.drop_stop else "Drop",
        fare=booking.fare_amount,
        status=booking.status,
        created_at=booking.created_at
    )

