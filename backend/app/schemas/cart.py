"""
LPU GoCart - Cart & Seating Schemas
"""

from typing import List, Optional
from pydantic import BaseModel

class CartSeatSchema(BaseModel):
    id: str
    cart_id: str
    seat_number: int
    seat_label: str
    is_accessible: bool
    is_available: bool = True
    is_locked: bool = False

    class Config:
        from_attributes = True

class CartSummarySchema(BaseModel):
    id: str
    cart_number: str
    model: str
    total_seats: int
    available_seats: int = 8
    battery_percentage: int
    status: str
    current_route_id: Optional[str] = None
    route_name: Optional[str] = None
    route_code: Optional[str] = None
    has_cctv: bool = False
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None

    class Config:
        from_attributes = True

class CartDetailSchema(CartSummarySchema):
    seats: List[CartSeatSchema] = []
    assigned_driver_name: Optional[str] = None
    assigned_driver_phone: Optional[str] = None
    cctv_is_online: Optional[bool] = None

class CartCreateRequest(BaseModel):
    cart_number: str
    model: str = "Club Car Transporter 8"
    total_seats: int = 8
    battery_percentage: int = 100
    status: str = "ACTIVE"
    current_route_id: Optional[str] = None
    has_cctv: bool = False

