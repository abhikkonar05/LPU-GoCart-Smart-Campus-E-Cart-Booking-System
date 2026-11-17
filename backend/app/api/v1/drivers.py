"""
LPU GoCart - Driver Operations REST Router
Handles driver trip shifts, passenger manifest, and QR ticket scanning.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Cart, Trip, Booking, User
from app.services.qr_service import verify_and_redeem_ticket
from app.core.dependencies import get_current_driver

router = APIRouter(prefix="/drivers", tags=["Driver Operations"])

class StartTripRequest(BaseModel):
    cart_id: str
    route_id: Optional[str] = None

class EndTripRequest(BaseModel):
    trip_id: str

class ScanQRRequest(BaseModel):
    qr_token: str

@router.get("/assigned-cart")
def get_driver_assigned_cart(
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """Fetch assigned vehicle and currently active trip for driver."""
    cart = db.query(Cart).filter(Cart.driver_id == current_driver.id).first()
    
    # If not assigned, assign first available cart for testing
    if not cart:
        cart = db.query(Cart).filter(Cart.driver_id == None).first()
        if not cart:
            cart = db.query(Cart).first()
        if cart:
            cart.driver_id = current_driver.id
            db.commit()
            db.refresh(cart)

    active_trip = None
    if cart:
        active_trip = db.query(Trip).filter(
            Trip.cart_id == cart.id,
            Trip.driver_id == current_driver.id,
            Trip.status.in_(["SCHEDULED", "ACTIVE"])
        ).first()

    return {
        "driver_id": current_driver.id,
        "full_name": current_driver.full_name,
        "phone_number": current_driver.phone_number,
        "assigned_cart": {
            "id": cart.id if cart else None,
            "cart_number": cart.cart_number if cart else "Unassigned",
            "name": cart.name if cart else "",
            "battery_percentage": cart.battery_percentage if cart else 100,
            "cart_status": cart.cart_status if cart else "OFFLINE",
            "current_route_id": cart.current_route_id if cart else None,
            "route_name": cart.current_route.name if cart and cart.current_route else None
        } if cart else None,
        "active_trip": {
            "id": active_trip.id if active_trip else None,
            "status": active_trip.status if active_trip else None,
            "started_at": active_trip.started_at if active_trip else None
        } if active_trip else None
    }

@router.post("/trips/start")
def start_trip(
    req: StartTripRequest,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """Start a new transit trip on assigned route."""
    now = datetime.now(timezone.utc)
    cart = db.query(Cart).filter(Cart.id == req.cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")

    route_id = req.route_id or cart.current_route_id
    if not route_id:
        from app.database.models import Route
        r = db.query(Route).first()
        route_id = r.id if r else None

    # Check for existing scheduled trip or create new
    trip = db.query(Trip).filter(
        Trip.cart_id == cart.id,
        Trip.status == "SCHEDULED"
    ).first()

    if trip:
        trip.status = "ACTIVE"
        trip.started_at = now
        trip.driver_id = current_driver.id
    else:
        trip = Trip(
            cart_id=cart.id,
            driver_id=current_driver.id,
            route_id=route_id,
            status="ACTIVE",
            started_at=now
        )
        db.add(trip)
    
    cart.cart_status = "ON_TRIP"
    cart.gps_status = "LIVE"
    cart.driver_id = current_driver.id
    if route_id:
        cart.current_route_id = route_id

    db.commit()
    db.refresh(trip)

    return {
        "trip_id": trip.id,
        "cart_id": trip.cart_id,
        "status": trip.status,
        "started_at": trip.started_at
    }

@router.post("/trips/end")
def end_trip(
    req: EndTripRequest,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """Complete an active trip."""
    trip = db.query(Trip).filter(Trip.id == req.trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    trip.status = "COMPLETED"
    trip.completed_at = datetime.now(timezone.utc)

    cart = db.query(Cart).filter(Cart.id == trip.cart_id).first()
    if cart:
        cart.cart_status = "AVAILABLE"
        cart.gps_status = "STOPPED"

    db.commit()

    return {"message": "Trip marked as completed.", "trip_id": trip.id}

@router.post("/verify-qr")
def scan_and_verify_qr(
    req: ScanQRRequest,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """Scan and redeem passenger digital boarding pass."""
    result = verify_and_redeem_ticket(
        db=db,
        qr_token=req.qr_token,
        driver_id=current_driver.id
    )
    if not result["valid"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
    return result

@router.get("/passengers")
def get_trip_passengers(
    trip_id: str,
    current_driver: User = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """Passenger manifest for driver showing confirmed and boarded riders."""
    bookings = db.query(Booking).filter(
        Booking.trip_id == trip_id,
        Booking.status.in_(["CONFIRMED", "CHECKED_IN", "BOARDED"])
    ).all()

    return [
        {
            "booking_id": b.id,
            "booking_code": b.booking_code,
            "passenger_name": b.user.full_name if b.user else "Passenger",
            "phone_number": b.user.phone_number if b.user else None,
            "seat_label": b.seat.seat_label if b.seat else (f"Full Cart" if b.booking_type == "FULL_CART" else "General"),
            "booking_type": b.booking_type,
            "pickup_stop": b.pickup_stop.name if b.pickup_stop else "Pickup",
            "drop_stop": b.drop_stop.name if b.drop_stop else "Drop",
            "status": b.status
        }
        for b in bookings
    ]
