"""
LPU GoCart - SQLAlchemy Relational ORM Models
Matches the 18 tables defined in the Master Project Architecture.
Roles: ADMIN, DRIVER, CUSTOMER
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database.connection import Base

def generate_uuid() -> str:
    """Generate string UUIDv4 for SQLite & PostgreSQL compatibility."""
    return str(uuid.uuid4())

def utc_now() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)

# 1. Users Table (ADMIN, DRIVER, CUSTOMER)
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    role = Column(String(20), nullable=False, default="CUSTOMER") # ADMIN, DRIVER, CUSTOMER
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    assigned_cart = relationship("Cart", back_populates="driver", foreign_keys="Cart.driver_id", uselist=False)
    trips = relationship("Trip", back_populates="driver", foreign_keys="Trip.driver_id")
    bookings = relationship("Booking", back_populates="user", foreign_keys="Booking.user_id")
    notifications = relationship("Notification", back_populates="user")

# 2. Routes Table
class Route(Base):
    __tablename__ = "routes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False) # e.g. "Main Gate - UniMall Express"
    code = Column(String(20), unique=True, nullable=False, index=True) # "ROUTE-A"
    start_point = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    fare_amount = Column(Float, default=10.0, nullable=False)
    estimated_duration_minutes = Column(Integer, default=15, nullable=False)
    distance_km = Column(Float, default=2.5, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    stops = relationship("RouteStop", back_populates="route", order_by="RouteStop.sequence_order", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="current_route")
    trips = relationship("Trip", back_populates="route")

# 3. Route Stops Table
class RouteStop(Base):
    __tablename__ = "route_stops"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    route_id = Column(String(36), ForeignKey("routes.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    sequence_order = Column(Integer, nullable=False)
    estimated_minutes = Column(Integer, default=2, nullable=False)

    route = relationship("Route", back_populates="stops")
    __table_args__ = (UniqueConstraint("route_id", "sequence_order", name="uq_route_stop_seq"),)

# 4. Carts Table (Unique ID e.g. "LPU-GC-001")
class Cart(Base):
    __tablename__ = "carts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_number = Column(String(30), unique=True, nullable=False, index=True) # "LPU-GC-001"
    name = Column(String(100), nullable=False) # "Express Green 1"
    model = Column(String(50), default="Club Car Transporter 6", nullable=False)
    total_passenger_seats = Column(Integer, default=6, nullable=False)
    luggage_capacity_small = Column(Integer, default=4, nullable=False)
    luggage_capacity_medium = Column(Integer, default=3, nullable=False)
    luggage_capacity_large = Column(Integer, default=2, nullable=False)
    current_route_id = Column(String(36), ForeignKey("routes.id", ondelete="SET NULL"), nullable=True)
    driver_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    battery_percentage = Column(Integer, default=100, nullable=False)
    cart_status = Column(String(20), default="AVAILABLE", nullable=False) # AVAILABLE, ASSIGNED, ON_TRIP, FULL, MAINTENANCE, OFFLINE
    gps_status = Column(String(20), default="OFFLINE", nullable=False) # LIVE, STOPPED, OFFLINE
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    driver = relationship("User", back_populates="assigned_cart", foreign_keys=[driver_id])
    current_route = relationship("Route", back_populates="carts")
    seats = relationship("CartSeat", back_populates="cart", order_by="CartSeat.seat_number", cascade="all, delete-orphan")
    trips = relationship("Trip", back_populates="cart")
    gps_logs = relationship("GPSLocation", back_populates="cart", cascade="all, delete-orphan")

# 5. Cart Seats Table
class CartSeat(Base):
    __tablename__ = "cart_seats"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    seat_number = Column(Integer, nullable=False) # 1 to 6
    seat_label = Column(String(10), nullable=False) # "S1", "S2"
    is_accessible = Column(Boolean, default=False, nullable=False)

    cart = relationship("Cart", back_populates="seats")
    seat_locks = relationship("SeatLock", back_populates="seat")
    bookings = relationship("Booking", back_populates="seat")
    __table_args__ = (UniqueConstraint("cart_id", "seat_number", name="uq_cart_seat_num"),)

# 6. Trips Table
class Trip(Base):
    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    driver_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    route_id = Column(String(36), ForeignKey("routes.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String(20), default="SCHEDULED", nullable=False) # SCHEDULED, ACTIVE, COMPLETED, CANCELLED
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    cart = relationship("Cart", back_populates="trips")
    driver = relationship("User", back_populates="trips", foreign_keys=[driver_id])
    route = relationship("Route", back_populates="trips")
    bookings = relationship("Booking", back_populates="trip")
    seat_locks = relationship("SeatLock", back_populates="trip")
    cart_locks = relationship("CartLock", back_populates="trip")

# 7. Seat Locks (Atomic 5-Minute Holds)
class SeatLock(Base):
    __tablename__ = "seat_locks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    seat_id = Column(String(36), ForeignKey("cart_seats.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    locked_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_released = Column(Boolean, default=False, nullable=False)

    trip = relationship("Trip", back_populates="seat_locks")
    seat = relationship("CartSeat", back_populates="seat_locks")

# 8. Cart Locks (Full Cart Reservation Holds)
class CartLock(Base):
    __tablename__ = "cart_locks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    locked_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_released = Column(Boolean, default=False, nullable=False)

    trip = relationship("Trip", back_populates="cart_locks")

# 9. Bookings Table (Individual Seat or Full Cart)
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_code = Column(String(25), unique=True, nullable=False, index=True) # e.g. "LPU-BK-981203"
    user_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="RESTRICT"), nullable=False, index=True)
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="RESTRICT"), nullable=False)
    booking_type = Column(String(20), default="SEAT", nullable=False) # SEAT, FULL_CART
    pickup_stop_id = Column(String(36), ForeignKey("route_stops.id", ondelete="RESTRICT"), nullable=False)
    drop_stop_id = Column(String(36), ForeignKey("route_stops.id", ondelete="RESTRICT"), nullable=False)
    seat_id = Column(String(36), ForeignKey("cart_seats.id", ondelete="SET NULL"), nullable=True)
    total_amount = Column(Float, nullable=False, default=10.0)
    status = Column(String(20), default="PENDING", nullable=False, index=True) # PENDING, CONFIRMED, CHECKED_IN, COMPLETED, CANCELLED
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="bookings", foreign_keys=[user_id])
    trip = relationship("Trip", back_populates="bookings")
    seat = relationship("CartSeat", back_populates="bookings")
    pickup_stop = relationship("RouteStop", foreign_keys=[pickup_stop_id])
    drop_stop = relationship("RouteStop", foreign_keys=[drop_stop_id])
    luggage = relationship("LuggageBooking", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    qr_ticket = relationship("QRTicket", back_populates="booking", uselist=False, cascade="all, delete-orphan")

# 10. Luggage Bookings Table
class LuggageBooking(Base):
    __tablename__ = "luggage_bookings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    small_bags = Column(Integer, default=0, nullable=False)
    medium_bags = Column(Integer, default=0, nullable=False)
    large_bags = Column(Integer, default=0, nullable=False)
    luggage_fee = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    booking = relationship("Booking", back_populates="luggage")

# 11. Payments Table
class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    gateway = Column(String(20), default="demo", nullable=False) # demo, razorpay
    gateway_order_id = Column(String(100), nullable=True)
    gateway_payment_id = Column(String(100), nullable=True)
    status = Column(String(20), default="PENDING", nullable=False) # PENDING, COMPLETED, FAILED, REFUNDED
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    booking = relationship("Booking", back_populates="payment")

# 12. QR Tickets Table
class QRTicket(Base):
    __tablename__ = "qr_tickets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    qr_token = Column(Text, unique=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by_driver_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    booking = relationship("Booking", back_populates="qr_ticket")

# 13. GPS Locations Table (HTML5 Geolocation telemetry from driver phone)
class GPSLocation(Base):
    __tablename__ = "gps_locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    driver_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy_meters = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    cart = relationship("Cart", back_populates="gps_logs")

# 14. Notifications Table
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("User", back_populates="notifications")

# 15. Audit Logs Table
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
