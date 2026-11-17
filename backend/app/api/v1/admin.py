"""
LPU GoCart - Administrative REST Router
Fleet control, analytics metrics, and user & booking governance.
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.connection import get_db
from app.database.models import (
    Cart, CartSeat, Route, Trip, Booking, Payment, User
)
from app.schemas.admin import FleetMetricsResponse, AdminCartUpdateRequest
from app.schemas.cart import CartCreateRequest
from app.core.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin Fleet Management"])

@router.get("/metrics", response_model=FleetMetricsResponse)
def get_fleet_metrics(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Real-time campus fleet operational metrics calculated from database."""
    total_carts = db.query(Cart).count()
    active_carts = db.query(Cart).filter(Cart.cart_status.in_(["AVAILABLE", "ASSIGNED", "ON_TRIP"])).count()
    active_trips = db.query(Trip).filter(Trip.status == "ACTIVE").count()
    total_students = db.query(User).filter(User.role == "CUSTOMER").count()
    total_drivers = db.query(User).filter(User.role == "DRIVER").count()
    
    # Calculate available seats across all active carts
    total_seats = db.query(func.sum(Cart.total_passenger_seats)).filter(
        Cart.cart_status.in_(["AVAILABLE", "ASSIGNED", "ON_TRIP"])
    ).scalar() or 0
    
    booked_seats = db.query(Booking).filter(
        Booking.status.in_(["CONFIRMED", "CHECKED_IN", "BOARDED"])
    ).count()
    avail_seats = max(0, total_seats - booked_seats)

    # Today's bookings and revenue
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_bookings = db.query(Booking).filter(Booking.created_at >= today_start).count()
    today_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "COMPLETED",
        Payment.created_at >= today_start
    ).scalar() or 0.0

    return FleetMetricsResponse(
        total_carts=total_carts,
        active_carts=active_carts,
        active_trips=active_trips,
        available_seats=avail_seats,
        total_students=total_students,
        total_drivers=total_drivers,
        total_bookings_today=today_bookings,
        total_revenue_today=float(today_revenue),
        cctv_online_count=0
    )

@router.get("/carts")
def list_all_carts_admin(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all carts with complete configuration and driver assignments."""
    carts = db.query(Cart).all()
    return [
        {
            "id": c.id,
            "cart_number": c.cart_number,
            "name": c.name,
            "model": c.model,
            "total_passenger_seats": c.total_passenger_seats,
            "battery_percentage": c.battery_percentage,
            "cart_status": c.cart_status,
            "gps_status": c.gps_status,
            "driver_name": c.driver.full_name if c.driver else None,
            "driver_id": c.driver_id,
            "route_name": c.current_route.name if c.current_route else None,
            "route_code": c.current_route.code if c.current_route else None,
            "current_route_id": c.current_route_id
        }
        for c in carts
    ]

@router.post("/carts", status_code=status.HTTP_201_CREATED)
def register_new_cart(
    req: CartCreateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Add a new e-cart to campus inventory and automatically provision its 6 seats."""
    clean_number = req.cart_number.strip().upper()
    existing = db.query(Cart).filter(Cart.cart_number == clean_number).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart number already registered.")

    cart = Cart(
        cart_number=clean_number,
        name=req.name,
        model=req.model,
        total_passenger_seats=req.total_passenger_seats,
        battery_percentage=req.battery_percentage,
        cart_status=req.cart_status,
        current_route_id=req.current_route_id
    )
    db.add(cart)
    db.flush()

    # Automatically provision seats S1 through S6
    for i in range(1, req.total_passenger_seats + 1):
        seat = CartSeat(
            cart_id=cart.id,
            seat_number=i,
            seat_label=f"S{i}",
            is_accessible=(i == 1)
        )
        db.add(seat)

    db.commit()
    db.refresh(cart)
    return {"message": f"Cart {cart.cart_number} successfully registered with {req.total_passenger_seats} seats.", "id": cart.id}

@router.put("/carts/{cart_id}")
def update_cart_info(
    cart_id: str,
    req: AdminCartUpdateRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update cart status, battery level, driver, or route assignment."""
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found.")

    if req.name is not None:
        cart.name = req.name
    if req.cart_status is not None:
        cart.cart_status = req.cart_status
    if req.battery_percentage is not None:
        cart.battery_percentage = req.battery_percentage
    if req.current_route_id is not None:
        cart.current_route_id = req.current_route_id
    if req.driver_id is not None:
        cart.driver_id = req.driver_id

    db.commit()
    return {"message": f"Cart {cart.cart_number} updated successfully."}

@router.get("/users")
def list_users(
    role: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List users filtered by role (CUSTOMER, DRIVER, ADMIN)."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role.upper())
    users = query.all()
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "phone_number": u.phone_number,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at
        }
        for u in users
    ]

@router.get("/bookings")
def list_all_bookings(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all student and guest bookings campus-wide."""
    bookings = db.query(Booking).order_by(Booking.created_at.desc()).limit(100).all()
    return [
        {
            "id": b.id,
            "booking_code": b.booking_code,
            "passenger_name": b.user.full_name if b.user else "Passenger",
            "cart_number": b.cart.cart_number if b.cart else "N/A",
            "booking_type": b.booking_type,
            "fare_amount": b.total_amount,
            "status": b.status,
            "pickup": b.pickup_stop.name if b.pickup_stop else "Pickup",
            "drop": b.drop_stop.name if b.drop_stop else "Drop",
            "created_at": b.created_at
        }
        for b in bookings
    ]
