"""
LPU GoCart - Administrative REST Router
Fleet control, analytics metrics, CCTV monitors, and user governance.
"""

from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.connection import get_db
from app.database.models.models import (
    Cart, CartSeat, Route, Trip, Booking, Payment, Profile, Student, Driver, CCTVDevice
)
from app.schemas.admin import FleetMetricsResponse, CCTVDeviceSchema, AdminCartUpdateRequest
from app.schemas.cart import CartCreateRequest, CartDetailSchema
from app.core.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin Fleet Management"])

@router.get("/metrics", response_model=FleetMetricsResponse)
def get_fleet_metrics(
    current_admin: Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Real-time campus fleet operational metrics calculated from database."""
    total_carts = db.query(Cart).count()
    active_carts = db.query(Cart).filter(Cart.status == "ACTIVE").count()
    active_trips = db.query(Trip).filter(Trip.status == "IN_TRANSIT").count()
    total_students = db.query(Student).count()
    total_drivers = db.query(Driver).count()
    
    # Calculate available seats across all active carts
    total_seats = db.query(func.sum(Cart.total_seats)).filter(Cart.status == "ACTIVE").scalar() or 0
    now = datetime.now(timezone.utc)
    booked_seats = db.query(Booking).filter(
        Booking.status.in_(["CONFIRMED", "BOARDED"])
    ).count()
    avail_seats = max(0, total_seats - booked_seats)

    # Today's bookings and revenue
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_bookings = db.query(Booking).filter(Booking.created_at >= today_start).count()
    today_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "COMPLETED",
        Payment.created_at >= today_start
    ).scalar() or 0.0

    cctv_online = db.query(CCTVDevice).filter(CCTVDevice.is_online == True).count()

    return FleetMetricsResponse(
        total_carts=total_carts,
        active_carts=active_carts,
        active_trips=active_trips,
        available_seats=avail_seats,
        total_students=total_students,
        total_drivers=total_drivers,
        total_bookings_today=today_bookings,
        total_revenue_today=float(today_revenue),
        cctv_online_count=cctv_online
    )

@router.post("/carts", status_code=status.HTTP_201_CREATED)
def register_new_cart(
    req: CartCreateRequest,
    current_admin: Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Add a new e-cart to campus inventory and automatically provision its 8 seats."""
    existing = db.query(Cart).filter(Cart.cart_number == req.cart_number.upper()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart number already registered.")

    cart = Cart(
        cart_number=req.cart_number.upper(),
        model=req.model,
        total_seats=req.total_seats,
        battery_percentage=req.battery_percentage,
        status=req.status,
        current_route_id=req.current_route_id,
        has_cctv=req.has_cctv
    )
    db.add(cart)
    db.flush()

    # Automatically provision seats S1 through S8
    for i in range(1, req.total_seats + 1):
        seat = CartSeat(
            cart_id=cart.id,
            seat_number=i,
            seat_label=f"S{i}",
            is_accessible=(i == 1)
        )
        db.add(seat)

    db.commit()
    db.refresh(cart)
    return {"message": f"Cart {cart.cart_number} successfully registered with {req.total_seats} seats.", "id": cart.id}

@router.put("/carts/{cart_id}")
def update_cart_info(
    cart_id: str,
    req: AdminCartUpdateRequest,
    current_admin: Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update cart status, battery level, or route assignment."""
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found.")

    if req.status is not None:
        cart.status = req.status
    if req.battery_percentage is not None:
        cart.battery_percentage = req.battery_percentage
    if req.current_route_id is not None:
        cart.current_route_id = req.current_route_id
    if req.has_cctv is not None:
        cart.has_cctv = req.has_cctv

    db.commit()
    return {"message": f"Cart {cart.cart_number} updated successfully."}

@router.get("/cctv", response_model=List[CCTVDeviceSchema])
def list_cctv_devices(
    current_admin: Profile = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all registered cart CCTV camera units and connectivity health."""
    devices = db.query(CCTVDevice).all()
    return [
        CCTVDeviceSchema(
            id=d.id,
            cart_id=d.cart_id,
            cart_number=d.cart.cart_number if d.cart else "Unassigned",
            device_serial=d.device_serial,
            stream_url=d.stream_url,
            stream_protocol=d.stream_protocol,
            is_online=d.is_online,
            last_heartbeat=d.last_heartbeat
        )
        for d in devices
    ]

