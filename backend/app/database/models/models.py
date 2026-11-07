"""
LPU GoCart - SQLAlchemy 2.0 Relational ORM Models
Defines tables matching the Supabase PostgreSQL schema with complete constraints and relationships.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.database.connection import Base

def generate_uuid() -> str:
    """Generate string UUIDv4 for cross-database compatibility (Postgres/SQLite)."""
    return str(uuid.uuid4())

def utc_now() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)

# 1. User Profiles
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    role = Column(String(20), nullable=False, default="STUDENT") # STUDENT, DRIVER, ADMIN
    avatar_url = Column(Text, nullable=True)
    hashed_password = Column(String(255), nullable=True) # Used for local auth / dev mode
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    student = relationship("Student", back_populates="profile", uselist=False, cascade="all, delete-orphan")
    driver = relationship("Driver", back_populates="profile", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="recipient", cascade="all, delete-orphan")

# 2. Student Extensions
class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    registration_number = Column(String(30), unique=True, nullable=False, index=True) # e.g. "12104567"
    department = Column(String(100), nullable=True)
    hostel_block = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    profile = relationship("Profile", back_populates="student")
    bookings = relationship("Booking", back_populates="student")
    seat_locks = relationship("SeatLock", back_populates="student")

# 3. Driver Extensions
class Driver(Base):
    __tablename__ = "drivers"

    id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    license_number = Column(String(50), unique=True, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    assigned_cart_id = Column(String(36), ForeignKey("carts.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    profile = relationship("Profile", back_populates="driver")
    assigned_cart = relationship("Cart", back_populates="assigned_driver", foreign_keys=[assigned_cart_id])
    trips = relationship("Trip", back_populates="driver")

# 4. Campus Routes
class Route(Base):
    __tablename__ = "routes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False) # e.g., "Main Gate - UniMall Express"
    code = Column(String(20), unique=True, nullable=False, index=True) # "ROUTE-A"
    description = Column(Text, nullable=True)
    fare_amount = Column(Float, default=10.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    stops = relationship("RouteStop", back_populates="route", order_by="RouteStop.sequence_order", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="current_route")
    trips = relationship("Trip", back_populates="route")

# 5. Route Stops
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
    __table_args__ = (UniqueConstraint("route_id", "sequence_order", name="uq_route_stop_order"),)

# 6. Electric Carts
class Cart(Base):
    __tablename__ = "carts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_number = Column(String(20), unique=True, nullable=False, index=True) # "LPU-CART-01"
    model = Column(String(50), default="Club Car Transporter 8", nullable=False)
    total_seats = Column(Integer, default=8, nullable=False)
    battery_percentage = Column(Integer, default=100, nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False) # ACTIVE, MAINTENANCE, OFFLINE, CHARGING
    current_route_id = Column(String(36), ForeignKey("routes.id", ondelete="SET NULL"), nullable=True)
    has_cctv = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    current_route = relationship("Route", back_populates="carts")
    seats = relationship("CartSeat", back_populates="cart", order_by="CartSeat.seat_number", cascade="all, delete-orphan")
    assigned_driver = relationship("Driver", back_populates="assigned_cart", foreign_keys=[Driver.assigned_cart_id], uselist=False)
    trips = relationship("Trip", back_populates="cart")
    cctv_device = relationship("CCTVDevice", back_populates="cart", uselist=False, cascade="all, delete-orphan")
    gps_logs = relationship("GPSLocation", back_populates="cart", cascade="all, delete-orphan")

# 7. Cart Seats
class CartSeat(Base):
    __tablename__ = "cart_seats"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    seat_number = Column(Integer, nullable=False) # 1 to 8
    seat_label = Column(String(10), nullable=False) # "S1", "S2"
    is_accessible = Column(Boolean, default=False, nullable=False)

    cart = relationship("Cart", back_populates="seats")
    seat_locks = relationship("SeatLock", back_populates="seat")
    bookings = relationship("Booking", back_populates="seat")
    __table_args__ = (UniqueConstraint("cart_id", "seat_number", name="uq_cart_seat_num"),)

# 8. Trips
class Trip(Base):
    __tablename__ = "trips"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    driver_id = Column(String(36), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True)
    route_id = Column(String(36), ForeignKey("routes.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String(20), default="SCHEDULED", nullable=False) # SCHEDULED, IN_TRANSIT, COMPLETED, CANCELLED
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    cart = relationship("Cart", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    route = relationship("Route", back_populates="trips")
    bookings = relationship("Booking", back_populates="trip")
    seat_locks = relationship("SeatLock", back_populates="trip")

# 9. Seat Locks (Atomic 5-Minute Holds)
class SeatLock(Base):
    __tablename__ = "seat_locks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    seat_id = Column(String(36), ForeignKey("cart_seats.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    locked_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_released = Column(Boolean, default=False, nullable=False)

    trip = relationship("Trip", back_populates="seat_locks")
    seat = relationship("CartSeat", back_populates="seat_locks")
    student = relationship("Student", back_populates="seat_locks")

# 10. Bookings
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_code = Column(String(20), unique=True, nullable=False, index=True) # e.g. "LPU-BK-918231"
    student_id = Column(String(36), ForeignKey("students.id", ondelete="RESTRICT"), nullable=False, index=True)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="RESTRICT"), nullable=False, index=True)
    seat_id = Column(String(36), ForeignKey("cart_seats.id", ondelete="RESTRICT"), nullable=False)
    pickup_stop_id = Column(String(36), ForeignKey("route_stops.id", ondelete="RESTRICT"), nullable=False)
    drop_stop_id = Column(String(36), ForeignKey("route_stops.id", ondelete="RESTRICT"), nullable=False)
    fare_amount = Column(Float, nullable=False)
    status = Column(String(20), default="PENDING", nullable=False, index=True) # PENDING, CONFIRMED, BOARDED, CANCELLED, EXPIRED
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    student = relationship("Student", back_populates="bookings")
    trip = relationship("Trip", back_populates="bookings")
    seat = relationship("CartSeat", back_populates="bookings")
    pickup_stop = relationship("RouteStop", foreign_keys=[pickup_stop_id])
    drop_stop = relationship("RouteStop", foreign_keys=[drop_stop_id])
    payment = relationship("Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    qr_ticket = relationship("QRTicket", back_populates="booking", uselist=False, cascade="all, delete-orphan")

# 11. Payments
class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    gateway = Column(String(20), nullable=False) # 'demo' or 'razorpay'
    gateway_order_id = Column(String(100), nullable=True)
    gateway_payment_id = Column(String(100), nullable=True)
    status = Column(String(20), default="PENDING", nullable=False) # PENDING, COMPLETED, FAILED, REFUNDED
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    booking = relationship("Booking", back_populates="payment")

# 12. GPS Locations
class GPSLocation(Base):
    __tablename__ = "gps_locations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    driver_id = Column(String(36), ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False)
    trip_id = Column(String(36), ForeignKey("trips.id", ondelete="SET NULL"), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed_kph = Column(Float, default=0.0)
    heading = Column(Float, nullable=True)
    accuracy_meters = Column(Float, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    cart = relationship("Cart", back_populates="gps_logs")

# 13. QR Boarding Tickets
class QRTicket(Base):
    __tablename__ = "qr_tickets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    qr_token = Column(Text, unique=True, nullable=False, index=True)
    is_used = Column(Boolean, default=False, nullable=False)
    scanned_at = Column(DateTime(timezone=True), nullable=True)
    scanned_by_driver_id = Column(String(36), ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    booking = relationship("Booking", back_populates="qr_ticket")

# 14. CCTV Devices
class CCTVDevice(Base):
    __tablename__ = "cctv_devices"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="CASCADE"), unique=True, nullable=False)
    device_serial = Column(String(100), unique=True, nullable=False)
    stream_url = Column(Text, nullable=True)
    stream_protocol = Column(String(20), default="RTSP", nullable=False)
    is_online = Column(Boolean, default=False, nullable=False)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    cart = relationship("Cart", back_populates="cctv_device")

# 15. Notifications
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    recipient_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    recipient = relationship("Profile", back_populates="notifications")

# 16. Audit Logs
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    actor_id = Column(String(36), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(50), nullable=True)
    metadata_json = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

