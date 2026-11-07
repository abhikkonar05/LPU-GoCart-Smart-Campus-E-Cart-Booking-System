"""
LPU GoCart - Campus Routes & Stops Schemas
"""

from typing import List, Optional
from pydantic import BaseModel

class RouteStopSchema(BaseModel):
    id: str
    route_id: str
    name: str
    latitude: float
    longitude: float
    sequence_order: int
    estimated_minutes: int

    class Config:
        from_attributes = True

class RouteSchema(BaseModel):
    id: str
    name: str
    code: str
    description: Optional[str] = None
    fare_amount: float
    is_active: bool
    stops: List[RouteStopSchema] = []

    class Config:
        from_attributes = True

class RouteCreateRequest(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    fare_amount: float = 10.0
    is_active: bool = True

