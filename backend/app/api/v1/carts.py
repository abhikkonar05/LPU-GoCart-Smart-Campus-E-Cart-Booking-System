"""
LPU GoCart - Electric Carts & Seating REST Router
"""

from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Cart, CartSeat, SeatLock, Booking, Trip
from app.schemas.cart import CartSummarySchema, CartDetailSchema, CartSeatSchema
from app.services.tracking_service import get_latest_cart_position
from app.services.seat_lock_service import clean_expired_locks

router = APIRouter(prefix="/carts", tags=["Fleet & Carts"])

@router.get("", response_model=List[CartSummarySchema])
def list_active_carts(db: Session = Depends(get_db)):
    """Fetch all campus e-carts with remaining available seats and live coordinates."""
    now = datetime.now(timezone.utc)
    clean_expired_locks(db)
    carts = db.query(Cart).filter(Cart.cart_status.in_(["AVAILABLE", "ASSIGNED", "ON_TRIP"])).all()
    
    result = []
    for c in carts:
        # Determine available seats by subtracting confirmed bookings and active locks
        active_trip = db.query(Trip).filter(
            Trip.cart_id == c.id,
            Trip.status.in_(["SCHEDULED", "ACTIVE"])
        ).first()

        occupied_count = 0
        if active_trip:
            # Confirmed bookings
            confirmed = db.query(Booking).filter(
                Booking.trip_id == active_trip.id,
                Booking.status.in_(["CONFIRMED", "CHECKED_IN", "BOARDED"])
            ).count()
            # Active 5-minute locks
            locked = db.query(SeatLock).filter(
                SeatLock.trip_id == active_trip.id,
                SeatLock.is_released == False
            ).count()
            occupied_count = confirmed + locked

        available_seats = max(0, c.total_passenger_seats - occupied_count)
        
        # Get live coordinates from in-memory telemetry cache
        pos = get_latest_cart_position(c.id)
        lat = pos.get("latitude") if pos else None
        lng = pos.get("longitude") if pos else None

        result.append(CartSummarySchema(
            id=c.id,
            cart_number=c.cart_number,
            name=c.name,
            model=c.model,
            total_seats=c.total_passenger_seats,
            available_seats=available_seats,
            battery_percentage=c.battery_percentage,
            status=c.cart_status,
            current_route_id=c.current_route_id,
            route_name=c.current_route.name if c.current_route else None,
            route_code=c.current_route.code if c.current_route else None,
            has_cctv=False,
            current_latitude=lat,
            current_longitude=lng
        ))
    return result

@router.get("/{cart_id}", response_model=CartDetailSchema)
def get_cart_detail(cart_id: str, db: Session = Depends(get_db)):
    """Fetch complete details of a specific cart including all individual seat statuses."""
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found.")

    now = datetime.now(timezone.utc)
    clean_expired_locks(db)

    active_trip = db.query(Trip).filter(
        Trip.cart_id == cart.id,
        Trip.status.in_(["SCHEDULED", "ACTIVE"])
    ).first()

    booked_seat_ids = set()
    locked_seat_ids = set()

    if active_trip:
        booked = db.query(Booking.seat_id).filter(
            Booking.trip_id == active_trip.id,
            Booking.status.in_(["CONFIRMED", "CHECKED_IN", "BOARDED"])
        ).all()
        booked_seat_ids = {b[0] for b in booked if b[0]}

        locks = db.query(SeatLock.seat_id).filter(
            SeatLock.trip_id == active_trip.id,
            SeatLock.is_released == False
        ).all()
        locked_seat_ids = {l[0] for l in locks if l[0]}

    seats_out = []
    available_count = 0
    for s in cart.seats:
        is_booked = s.id in booked_seat_ids
        is_locked = s.id in locked_seat_ids
        is_avail = not (is_booked or is_locked)
        if is_avail:
            available_count += 1
        
        seats_out.append(CartSeatSchema(
            id=s.id,
            cart_id=s.cart_id,
            seat_number=s.seat_number,
            seat_label=s.seat_label,
            is_accessible=s.is_accessible,
            is_available=is_avail,
            is_locked=is_locked
        ))

    pos = get_latest_cart_position(cart.id)
    lat = pos.get("latitude") if pos else None
    lng = pos.get("longitude") if pos else None

    driver_name = cart.driver.full_name if cart.driver else None
    driver_phone = cart.driver.phone_number if cart.driver else None

    return CartDetailSchema(
        id=cart.id,
        cart_number=cart.cart_number,
        name=cart.name,
        model=cart.model,
        total_seats=cart.total_passenger_seats,
        available_seats=available_count,
        battery_percentage=cart.battery_percentage,
        status=cart.cart_status,
        current_route_id=cart.current_route_id,
        route_name=cart.current_route.name if cart.current_route else None,
        route_code=cart.current_route.code if cart.current_route else None,
        has_cctv=False,
        current_latitude=lat,
        current_longitude=lng,
        seats=seats_out,
        assigned_driver_name=driver_name,
        assigned_driver_phone=driver_phone,
        luggage_capacity_small=cart.luggage_capacity_small,
        luggage_capacity_medium=cart.luggage_capacity_medium,
        luggage_capacity_large=cart.luggage_capacity_large
    )

@router.get("/{cart_id}/seats", response_model=List[CartSeatSchema])
def get_cart_seats(cart_id: str, db: Session = Depends(get_db)):
    """Fetch real-time seat map availability for a cart."""
    detail = get_cart_detail(cart_id, db)
    return detail.seats
