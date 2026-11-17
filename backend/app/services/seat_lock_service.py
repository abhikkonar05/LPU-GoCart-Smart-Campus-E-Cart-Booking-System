"""
LPU GoCart - Advanced Atomic Seat Locking System
Guarantees concurrency safety: prevents two users from locking or booking the same seat
for the same trip using database transaction locks and automatic timeout expiration.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from app.database.models import SeatLock, Booking, CartSeat, Trip
from app.core.config import settings

def to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def clean_expired_locks(db: Session, trip_id: Optional[str] = None):
    """
    Automatically release any seat locks that have surpassed their 5-minute duration.
    """
    now = datetime.now(timezone.utc)
    query = db.query(SeatLock).filter(SeatLock.is_released == False)
    if trip_id:
        query = query.filter(SeatLock.trip_id == trip_id)
    
    active_locks = query.all()
    expired = []
    for lock in active_locks:
        exp = to_utc(lock.expires_at)
        if exp and exp < now:
            lock.is_released = True
            expired.append(lock)
    
    if expired:
        db.commit()

def acquire_seat_lock(
    db: Session,
    trip_id: str,
    seat_id: str,
    user_id: str
) -> Tuple[bool, Optional[SeatLock], str]:
    """
    Atomically acquire a 5-minute hold on a seat.
    """
    now = datetime.now(timezone.utc)
    duration_mins = getattr(settings, "SEAT_LOCK_DURATION_MINUTES", 5)
    expires_at = now + timedelta(minutes=duration_mins)

    # 1. Clean expired locks for this trip first
    clean_expired_locks(db, trip_id)

    # 2. Check if seat is already CONFIRMED or CHECKED_IN
    confirmed_booking = db.query(Booking).filter(
        Booking.trip_id == trip_id,
        Booking.seat_id == seat_id,
        Booking.status.in_(["CONFIRMED", "CHECKED_IN", "BOARDED"])
    ).first()

    if confirmed_booking:
        return False, None, "This seat is already booked and confirmed by another passenger."

    # 3. Check if seat is currently locked by another user
    active_locks = db.query(SeatLock).filter(
        SeatLock.trip_id == trip_id,
        SeatLock.seat_id == seat_id,
        SeatLock.is_released == False
    ).all()

    for active_lock in active_locks:
        exp = to_utc(active_lock.expires_at)
        if exp and exp > now:
            if active_lock.user_id == user_id:
                active_lock.expires_at = expires_at
                db.commit()
                db.refresh(active_lock)
                return True, active_lock, "Seat lock extended for 5 minutes."
            else:
                remaining = max(1, int((exp - now).total_seconds()))
                return False, None, f"Seat is currently held by another passenger (resets in {remaining}s)."
        else:
            active_lock.is_released = True
            db.commit()

    # 4. Atomically create new seat lock
    new_lock = SeatLock(
        trip_id=trip_id,
        seat_id=seat_id,
        user_id=user_id,
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

def release_seat_lock(db: Session, lock_id: str, user_id: Optional[str] = None) -> bool:
    """Manually release a temporary seat lock."""
    query = db.query(SeatLock).filter(SeatLock.id == lock_id)
    if user_id:
        query = query.filter(SeatLock.user_id == user_id)
    lock = query.first()
    if lock:
        lock.is_released = True
        db.commit()
        return True
    return False
