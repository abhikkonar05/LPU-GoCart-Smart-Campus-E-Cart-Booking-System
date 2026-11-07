"""
LPU GoCart - Real-Time Telemetry REST Router
Receives GPS coordinates from driver smartphones and updates fleet position.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models.models import Cart, Driver, Profile
from app.schemas.tracking import GPSUpdateSchema
from app.services.tracking_service import (
    record_gps_telemetry, get_all_active_cart_positions, get_latest_cart_position
)
from app.websockets.tracking import ws_manager
from app.core.dependencies import get_current_driver

router = APIRouter(prefix="/tracking", tags=["Live Tracking & Telemetry"])

@router.post("/update")
async def update_cart_location(
    req: GPSUpdateSchema,
    current_driver_profile: Profile = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """
    Ingest GPS telemetry point from Driver Android App.
    Persists coordinate in database and broadcasts live position to students & admin web console.
    """
    cart = db.query(Cart).filter(Cart.id == req.cart_id).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found.")

    telemetry = record_gps_telemetry(
        db=db,
        cart_id=req.cart_id,
        driver_id=current_driver_profile.id,
        latitude=req.latitude,
        longitude=req.longitude,
        speed_kph=req.speed_kph or 0.0,
        heading=req.heading,
        accuracy_meters=req.accuracy_meters,
        trip_id=req.trip_id
    )

    # Broadcast to all connected WebSockets
    await ws_manager.broadcast_cart_update(
        cart_id=cart.id,
        cart_number=cart.cart_number,
        latitude=req.latitude,
        longitude=req.longitude,
        speed_kph=req.speed_kph or 0.0,
        heading=req.heading,
        battery=cart.battery_percentage,
        available_seats=cart.total_seats,
        route_code=cart.current_route.code if cart.current_route else None
    )

    return {"status": "OK", "recorded_at": telemetry["timestamp"]}

@router.get("/active")
def get_all_active_telemetry():
    """Fetch cached real-time coordinates for all operating campus carts."""
    return get_all_active_cart_positions()

@router.get("/cart/{cart_id}")
def get_cart_telemetry(cart_id: str):
    """Fetch latest coordinate for a specific cart."""
    pos = get_latest_cart_position(cart_id)
    if not pos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No GPS telemetry found for this cart.")
    return pos

