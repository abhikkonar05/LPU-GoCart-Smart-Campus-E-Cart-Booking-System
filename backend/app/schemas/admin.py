"""
LPU GoCart - Administrative Metrics & Fleet Schemas
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class FleetMetricsResponse(BaseModel):
    total_carts: int
    active_carts: int
    active_trips: int
    available_seats: int
    total_students: int
    total_drivers: int
    total_bookings_today: int
    total_revenue_today: float
    cctv_online_count: int

class CCTVDeviceSchema(BaseModel):
    id: str
    cart_id: str
    cart_number: str
    device_serial: str
    stream_url: Optional[str] = None
    stream_protocol: str = "RTSP"
    is_online: bool
    last_heartbeat: Optional[datetime] = None

    class Config:
        from_attributes = True

class AdminCartUpdateRequest(BaseModel):
    status: Optional[str] = None
    battery_percentage: Optional[int] = None
    current_route_id: Optional[str] = None
    has_cctv: Optional[bool] = None

