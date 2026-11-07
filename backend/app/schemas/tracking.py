"""
LPU GoCart - Real-Time Telemetry & Tracking Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class GPSUpdateSchema(BaseModel):
    cart_id: str
    trip_id: Optional[str] = None
    latitude: float
    longitude: float
    speed_kph: Optional[float] = 0.0
    heading: Optional[float] = None
    accuracy_meters: Optional[float] = None
    timestamp: Optional[datetime] = None

class CartTrackingBroadcastSchema(BaseModel):
    event: str = "CART_UPDATE"
    cart_id: str
    cart_number: str
    route_id: Optional[str] = None
    route_code: Optional[str] = None
    latitude: float
    longitude: float
    speed_kph: float = 0.0
    heading: Optional[float] = None
    battery_percentage: int = 100
    available_seats: int = 8
    next_stop_name: Optional[str] = None
    status: str = "ACTIVE"
    updated_at: datetime

