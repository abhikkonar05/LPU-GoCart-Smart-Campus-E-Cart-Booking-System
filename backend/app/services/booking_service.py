"""
LPU GoCart - Booking & Ticketing Lifecycle Service
Manages reservation lifecycle: PENDING -> CONFIRMED -> BOARDED / CANCELLED.
"""

import random
import string
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.database.models.models import Booking, SeatLock, QRTicket, Notification, CartSeat, Trip
from app.core.security import generate_qr_ticket_token

def generate_booking_code() -> str:
    """Generate a clean university booking reference code e.g. 'LPU-BK-839201'."""
    numbers = "".join(random.choices(string.digits, k=6))
    return f"LPU-BK-{numbers}"

def create_pending_booking(
    db: Session,
    student_id: str,
    lock_id: str,
    trip_id: str,
    seat_id: str,
    pickup_stop_id: str,
    drop_stop_id: str,
    fare_amount: float = 10.0
) -> Tuple[bool, Optional[Booking], str]:
    """Create a PENDING booking tied to a valid active seat lock."""
    now = datetime.now(timezone.utc)
    
    # 1. Verify seat lock belongs to this student and is active
    lock = db.query(SeatLock).filter(
        SeatLock.id == lock_id,
        SeatLock.student_id == student_id,
        SeatLock.is_released == False,
        SeatLock.expires_at > now
    ).first()

    if not lock:
        return False, None, "Seat lock has expired or is invalid. Please select your seat again."

    # 2. Generate unique booking code
    code = generate_booking_code()
    while db.query(Booking).filter(Booking.booking_code == code).first():
        code = generate_booking_code()

    # 3. Create booking record
    booking = Booking(
        booking_code=code,
        student_id=student_id,
        trip_id=trip_id,
        seat_id=seat_id,
        pickup_stop_id=pickup_stop_id,
        drop_stop_id=drop_stop_id,
        fare_amount=fare_amount,
        status="PENDING"
    )
    db.add(booking)
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
    Creates QR boarding ticket and notifies student.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        return False, None, "Booking not found."

    if booking.status in ["CONFIRMED", "BOARDED"]:
        return True, booking, "Booking is already confirmed."

    # Confirm booking
    booking.status = "CONFIRMED"

    # Release temporary lock (the booking record now holds the seat permanently)
    lock = db.query(SeatLock).filter(
        SeatLock.trip_id == booking.trip_id,
        SeatLock.seat_id == booking.seat_id,
        SeatLock.student_id == booking.student_id
    ).first()
    if lock:
        lock.is_released = True

    # Generate cryptographic QR token
    qr_token = generate_qr_ticket_token(booking.booking_code, booking.student_id, booking.trip_id)
    
    qr_ticket = db.query(QRTicket).filter(QRTicket.booking_id == booking.id).first()
    if not qr_ticket:
        qr_ticket = QRTicket(
            booking_id=booking.id,
            qr_token=qr_token,
            is_used=False
        )
        db.add(qr_ticket)

    # Issue student notification
    notif = Notification(
        recipient_id=booking.student_id,
        title="E-Cart Booking Confirmed!",
        message=f"Booking {booking.booking_code} confirmed! Present your QR boarding pass to the driver."
    )
    db.add(notif)

    db.commit()
    db.refresh(booking)
    return True, booking, "Booking confirmed and QR boarding pass issued."

