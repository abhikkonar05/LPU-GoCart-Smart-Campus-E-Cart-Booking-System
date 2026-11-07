"""
LPU GoCart - Driver Operations REST Router
Handles driver trip shifts, passenger manifest, and QR ticket scanning.
"""

from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models.models import Driver, Cart, Trip, Booking, Profile
from app.services.qr_service import verify_and_redeem_ticket
from app.core.dependencies import get_current_driver

router = APIRouter(prefix="/drivers", tags=["Driver Operations"])

class StartTripRequest(BaseModel):
    cart_id: str
    route_id: str

class EndTripRequest(BaseModel):
    trip_id: str

class ScanQRRequest(BaseModel):
    qr_token: str

@router.get("/assigned-cart")
def get_driver_assigned_cart(
    current_driver_profile: Profile = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """Fetch assigned vehicle and currently active trip for driver."""
    driver = db.query(Driver).filter(Driver.id == current_driver_profile.id).first()
    if not driver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver record not found.")

    cart = driver.assigned_cart
    # If not assigned, assign first available cart for testing
    if not cart:
        cart = db.query(Cart).filter(Cart.status == "ACTIVE").first()
        if cart:
            driver.assigned_cart_id = cart.id
            db.commit()

    active_trip = None
    if cart:
        active_trip = db.query(Trip).filter(
            Trip.cart_id == cart.id,
            Trip.driver_id == driver.id,
            Trip.status.in_(["SCHEDULED", "IN_TRANSIT"])
        ).first()

    return {
        "driver_id": driver.id,
        "full_name": current_driver_profile.full_name,
        "license_number": driver.license_number,
        "is_available": driver.is_available,
        "assigned_cart": {
            "id": cart.id if cart else None,
            "cart_number": cart.cart_number if cart else "Unassigned",
            "battery_percentage": cart.battery_percentage if cart else 100,
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
    current_driver_profile: Profile = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """Start a new transit trip on assigned route."""
    now = datetime.now(timezone.utc)
    trip = Trip(
        cart_id=req.cart_id,
        driver_id=current_driver_profile.id,
        route_id=req.route_id,
        status="IN_TRANSIT",
        started_at=now
    )
    db.add(trip)
    
    # Update cart status
    cart = db.query(Cart).filter(Cart.id == req.cart_id).first()
    if cart:
        cart.status = "ACTIVE"
        cart.current_route_id = req.route_id

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
    current_driver_profile: Profile = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """Complete an active trip."""
    trip = db.query(Trip).filter(Trip.id == req.trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")

    trip.status = "COMPLETED"
    trip.completed_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Trip marked as completed.", "trip_id": trip.id}

@router.post("/verify-qr")
def scan_and_verify_qr(
    req: ScanQRRequest,
    current_driver_profile: Profile = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """Scan and redeem student digital boarding pass."""
    result = verify_and_redeem_ticket(
        db=db,
        qr_token=req.qr_token,
        driver_id=current_driver_profile.id
    )
    if not result["valid"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])
    return result

@router.get("/passengers")
def get_trip_passengers(
    trip_id: str,
    current_driver_profile: Profile = Depends(get_current_driver),
    db: Session = Depends(get_db)
):
    """Passenger manifest for driver showing confirmed and boarded riders."""
    bookings = db.query(Booking).filter(
        Booking.trip_id == trip_id,
        Booking.status.in_(["CONFIRMED", "BOARDED"])
    ).all()

    return [
        {
            "booking_id": b.id,
            "booking_code": b.booking_code,
            "student_name": b.student.profile.full_name if b.student and b.student.profile else "Student",
            "phone_number": b.student.profile.phone_number if b.student and b.student.profile else None,
            "seat_label": b.seat.seat_label if b.seat else "S",
            "pickup_stop": b.pickup_stop.name if b.pickup_stop else "Pickup",
            "drop_stop": b.drop_stop.name if b.drop_stop else "Drop",
            "status": b.status
        }
        for b in bookings
    ]

