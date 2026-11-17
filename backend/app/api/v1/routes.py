"""
LPU GoCart - Campus Routes & Stops REST Router
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Route, RouteStop
from app.schemas.route import RouteSchema, RouteStopSchema

router = APIRouter(prefix="/routes", tags=["Routes & Stops"])

@router.get("", response_model=List[RouteSchema])
def list_routes(db: Session = Depends(get_db)):
    """Fetch all active LPU campus shuttle routes with their geocoded stop sequences."""
    routes = db.query(Route).filter(Route.is_active == True).all()
    result = []
    for r in routes:
        stops = [
            RouteStopSchema(
                id=s.id,
                route_id=s.route_id,
                name=s.name,
                latitude=s.latitude,
                longitude=s.longitude,
                sequence_order=s.sequence_order,
                estimated_minutes=s.estimated_minutes
            ) for s in r.stops
        ]
        result.append(RouteSchema(
            id=r.id,
            name=r.name,
            code=r.code,
            description=r.description,
            fare_amount=r.fare_amount,
            is_active=r.is_active,
            stops=stops
        ))
    return result

@router.get("/{route_id}", response_model=RouteSchema)
def get_route_detail(route_id: str, db: Session = Depends(get_db)):
    """Fetch single route and all its stops by ID."""
    route = db.query(Route).filter(Route.id == route_id).first()
    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found.")
    
    stops = [
        RouteStopSchema(
            id=s.id,
            route_id=s.route_id,
            name=s.name,
            latitude=s.latitude,
            longitude=s.longitude,
            sequence_order=s.sequence_order,
            estimated_minutes=s.estimated_minutes
        ) for s in route.stops
    ]
    return RouteSchema(
        id=route.id,
        name=route.name,
        code=route.code,
        description=route.description,
        fare_amount=route.fare_amount,
        is_active=route.is_active,
        stops=stops
    )
