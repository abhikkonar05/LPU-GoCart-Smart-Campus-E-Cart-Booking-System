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
    cctv_online_count: int = 0

class AdminCartUpdateRequest(BaseModel):
    name: Optional[str] = None
    cart_status: Optional[str] = None
    battery_percentage: Optional[int] = None
    current_route_id: Optional[str] = None
    driver_id: Optional[str] = None
