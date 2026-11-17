"""
LPU GoCart - Seat Locking & Booking Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SeatLockRequest(BaseModel):
    trip_id: str
    cart_id: str
    seat_id: str

class SeatLockResponse(BaseModel):
    lock_id: str
    trip_id: str
    seat_id: str
    seat_number: int
    seat_label: str
    locked_at: datetime
    expires_at: datetime
    remaining_seconds: int

class BookingCreateRequest(BaseModel):
    lock_id: Optional[str] = None
    trip_id: str
    cart_id: str
    seat_id: Optional[str] = None
    booking_type: str = "SEAT" # SEAT, FULL_CART
    pickup_stop_id: str
    drop_stop_id: str
    fare_amount: float = 10.0
    small_bags: int = 0
    medium_bags: int = 0
    large_bags: int = 0
    luggage_fee: float = 0.0

class BookingResponse(BaseModel):
    id: str
    booking_code: str
    user_id: str
    trip_id: str
    cart_id: str
    cart_number: str
    booking_type: str = "SEAT"
    seat_number: Optional[int] = None
    seat_label: Optional[str] = None
    pickup_stop_name: str
    drop_stop_name: str
    fare_amount: float
    status: str
    created_at: datetime
    qr_token: Optional[str] = None

    class Config:
        from_attributes = True

class TicketResponse(BaseModel):
    booking_id: str
    booking_code: str
    qr_token: str
    passenger_name: str
    cart_number: str
    seat_label: str
    booking_type: str = "SEAT"
    pickup_stop: str
    drop_stop: str
    fare: float
    status: str
    created_at: datetime
