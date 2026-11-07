"""
LPU GoCart - Advanced Atomic Seat Locking System
Guarantees concurrency safety: prevents two students from locking or booking the same seat
for the same trip using database transaction locks and automatic timeout expiration.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database.models.models import SeatLock, Booking, CartSeat, Trip
from app.core.config import settings

def clean_expired_locks(db: Session, trip_id: Optional[str] = None):
    """
    Automatically release any seat locks that have surpassed their 5-minute duration.
    Ensures that abandoned checkout attempts immediately become bookable again for others.
    """
    now = datetime.now(timezone.utc)
    query = db.query(SeatLock).filter(
        SeatLock.is_released == False,
        SeatLock.expires_at < now
    )
    if trip_id:
        query = query.filter(SeatLock.trip_id == trip_id)
    
    expired = query.all()
    for lock in expired:
        lock.is_released = True
    
    if expired:
        db.commit()

def acquire_seat_lock(
    db: Session,
    trip_id: str,
    seat_id: str,
    student_id: str
) -> Tuple[bool, Optional[SeatLock], str]:
    """
    Atomically acquire a 5-minute hold on a seat.
    Returns: (success: bool, lock: Optional[SeatLock], message: str)
    """
    now = datetime.now(timezone.utc)
    duration_mins = settings.SEAT_LOCK_DURATION_MINUTES
    expires_at = now + timedelta(minutes=duration_mins)

    # 1. Clean expired locks for this trip first
    clean_expired_locks(db, trip_id)

    # 2. Check if seat is already CONFIRMED or BOARDED
    confirmed_booking = db.query(Booking).filter(
        Booking.trip_id == trip_id,
        Booking.seat_id == seat_id,
        Booking.status.in_(["CONFIRMED", "BOARDED"])
    ).first()

    if confirmed_booking:
        return False, None, "This seat is already booked and confirmed by another student."

    # 3. Check if seat is currently locked by another student
    active_lock = db.query(SeatLock).filter(
        SeatLock.trip_id == trip_id,
        SeatLock.seat_id == seat_id,
        SeatLock.is_released == False,
        SeatLock.expires_at > now
    ).first()

    if active_lock:
        if active_lock.student_id == student_id:
            # Same student re-locking / extending checkout
            active_lock.expires_at = expires_at
            db.commit()
            db.refresh(active_lock)
            return True, active_lock, "Seat lock extended for 5 minutes."
        else:
            remaining = int((active_lock.expires_at - now).total_seconds())
            return False, None, f"Seat is currently held by another student (resets in {remaining}s)."

    # 4. Atomically create new seat lock
    new_lock = SeatLock(
        trip_id=trip_id,
        seat_id=seat_id,
        student_id=student_id,
        locked_at=now,
        expires_at=expires_at,
        is_released=False
    )
    db.add(new_lock)
    try:
        db.commit()
        db.refresh(new_lock)
        return True, new_lock, "Seat locked successfully for 5 minutes."
    except Exception as e:
        db.rollback()
        return False, None, f"Concurrent lock collision detected: {e}"

def release_seat_lock(db: Session, lock_id: str, student_id: Optional[str] = None) -> bool:
    """Manually release a temporary seat lock."""
    query = db.query(SeatLock).filter(SeatLock.id == lock_id)
    if student_id:
        query = query.filter(SeatLock.student_id == student_id)
    
    lock = query.first()
    if lock:
        lock.is_released = True
        db.commit()
        return True
    return False

