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
    name: Optional[str] = None
    model: str
    total_seats: int
    available_seats: int = 6
    battery_percentage: int
    status: str
    current_route_id: Optional[str] = None
    route_name: Optional[str] = None
    route_code: Optional[str] = None
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    has_cctv: bool = False

    class Config:
        from_attributes = True

class CartDetailSchema(CartSummarySchema):
    seats: List[CartSeatSchema] = []
    assigned_driver_name: Optional[str] = None
    assigned_driver_phone: Optional[str] = None
    luggage_capacity_small: int = 4
    luggage_capacity_medium: int = 3
    luggage_capacity_large: int = 2

class CartCreateRequest(BaseModel):
    cart_number: str
    name: str = "Campus Shuttle"
    model: str = "Club Car Transporter 6"
    total_passenger_seats: int = 6
    battery_percentage: int = 100
    cart_status: str = "AVAILABLE"
    current_route_id: Optional[str] = None
