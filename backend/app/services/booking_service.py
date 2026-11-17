"""
LPU GoCart - Booking & Ticketing Lifecycle Service
Manages reservation lifecycle: PENDING -> CONFIRMED -> CHECKED_IN / CANCELLED.
"""

import random
import string
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.database.models import Booking, SeatLock, QRTicket, Notification, CartSeat, Trip, Cart, LuggageBooking
from app.core.security import generate_qr_ticket_token

def generate_booking_code() -> str:
    """Generate a clean university booking reference code e.g. 'LPU-BK-839201'."""
    numbers = "".join(random.choices(string.digits, k=6))
    return f"LPU-BK-{numbers}"

def create_pending_booking(
    db: Session,
    user_id: str,
    lock_id: Optional[str],
    trip_id: str,
    cart_id: str,
    pickup_stop_id: str,
    drop_stop_id: str,
    seat_id: Optional[str] = None,
    booking_type: str = "SEAT",
    total_amount: float = 10.0,
    small_bags: int = 0,
    medium_bags: int = 0,
    large_bags: int = 0,
    luggage_fee: float = 0.0
) -> Tuple[bool, Optional[Booking], str]:
    """Create a PENDING booking tied to a valid active seat lock (if individual seat)."""
    now = datetime.now(timezone.utc)
    
    if booking_type == "SEAT" and lock_id:
        lock = db.query(SeatLock).filter(
            SeatLock.id == lock_id,
            SeatLock.user_id == user_id,
            SeatLock.is_released == False
        ).first()

        if lock:
            from app.services.seat_lock_service import to_utc
            exp = to_utc(lock.expires_at)
            if not exp or exp <= now:
                lock = None

        if not lock:
            return False, None, "Seat lock has expired or is invalid. Please select your seat again."

    # Generate unique booking code
    code = generate_booking_code()
    while db.query(Booking).filter(Booking.booking_code == code).first():
        code = generate_booking_code()

    # Create booking record
    booking = Booking(
        booking_code=code,
        user_id=user_id,
        trip_id=trip_id,
        cart_id=cart_id,
        booking_type=booking_type,
        pickup_stop_id=pickup_stop_id,
        drop_stop_id=drop_stop_id,
        seat_id=seat_id,
        total_amount=total_amount,
        status="PENDING"
    )
    db.add(booking)
    db.flush()

    # Optional luggage booking
    if small_bags > 0 or medium_bags > 0 or large_bags > 0:
        luggage = LuggageBooking(
            booking_id=booking.id,
            small_bags=small_bags,
            medium_bags=medium_bags,
            large_bags=large_bags,
            luggage_fee=luggage_fee
        )
        db.add(luggage)

    try:
        db.commit()
        db.refresh(booking)
        return True, booking, "Pending booking created. Proceed to payment."
    except Exception as e:
        db.rollback()
        return False, None, f"Could not create booking: {e}"

def confirm_booking_payment(
    db: Session,
    booking_id: str,
    payment_transaction_id: str
) -> Tuple[bool, Optional[Booking], str]:
    """
    Finalize a confirmed booking after verified payment success.
    Creates QR boarding ticket and notifies user.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        return False, None, "Booking not found."

    if booking.status in ["CONFIRMED", "CHECKED_IN", "BOARDED"]:
        return True, booking, "Booking is already confirmed."

    # Confirm booking
    booking.status = "CONFIRMED"

    # Release temporary lock (the booking record now holds the seat permanently)
    if booking.seat_id:
        lock = db.query(SeatLock).filter(
            SeatLock.trip_id == booking.trip_id,
            SeatLock.seat_id == booking.seat_id,
            SeatLock.user_id == booking.user_id
        ).first()
        if lock:
            lock.is_released = True

    # Generate cryptographic QR token
    qr_token = generate_qr_ticket_token(booking.booking_code, booking.user_id, booking.trip_id)
    
    qr_ticket = db.query(QRTicket).filter(QRTicket.booking_id == booking.id).first()
    if not qr_ticket:
        qr_ticket = QRTicket(
            booking_id=booking.id,
            qr_token=qr_token,
            is_verified=False
        )
        db.add(qr_ticket)

    # Issue notification
    notif = Notification(
        user_id=booking.user_id,
        title="E-Cart Booking Confirmed!",
        message=f"Booking {booking.booking_code} confirmed! Present your QR boarding pass to the driver."
    )
    db.add(notif)

    db.commit()
    db.refresh(booking)
    return True, booking, "Booking confirmed and QR boarding pass issued."
