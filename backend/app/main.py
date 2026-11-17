"""
LPU GoCart - Smart Campus E-Cart Booking & Tracking System
FastAPI Backend Application Entrypoint
Lovely Professional University (LPU), Phagwara, Punjab
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.database.connection import engine, Base, SessionLocal
from app.database.models.models import Route, RouteStop, Cart, CartSeat, Profile, Driver, Trip
from app.core.security import get_password_hash
from app.api.v1 import api_v1_router
from app.websockets.tracking import ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lpu_gocart")

def init_seed_data():
    """Seed initial LPU routes, stops, and carts if database is empty."""
    db = SessionLocal()
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)

        # Check if routes exist
        if db.query(Route).count() == 0:
            logger.info("[STARTUP] Seeding initial LPU routes and campus stops...")
            
            # Route A
            route_a = Route(
                name="Main Gate - UniMall Express",
                code="ROUTE-A",
                description="Direct express loop connecting Gate 1 with UniMall and Engineering Blocks",
                fare_amount=10.0,
                is_active=True
            )
            db.add(route_a)
            db.flush()

            stops_a = [
                RouteStop(route_id=route_a.id, name="Main Gate (Gate 1)", latitude=31.2538, longitude=75.7012, sequence_order=1, estimated_minutes=0),
                RouteStop(route_id=route_a.id, name="Block 32 (Engineering)", latitude=31.2545, longitude=75.7040, sequence_order=2, estimated_minutes=3),
                RouteStop(route_id=route_a.id, name="UniMall & Food Court", latitude=31.2529, longitude=75.7048, sequence_order=3, estimated_minutes=6),
                RouteStop(route_id=route_a.id, name="Central Library / Block 34", latitude=31.2552, longitude=75.7058, sequence_order=4, estimated_minutes=9),
            ]
            db.add_all(stops_a)

            # Route B
            route_b = Route(
                name="Hostels - Academic Loop",
                code="ROUTE-B",
                description="Frequent shuttle servicing Boys Hostels (BH) and Girls Hostels (GH)",
                fare_amount=10.0,
                is_active=True
            )
            db.add(route_b)
            db.flush()

            stops_b = [
                RouteStop(route_id=route_b.id, name="Boys Hostels (BH-1 to BH-8)", latitude=31.2568, longitude=75.7082, sequence_order=1, estimated_minutes=0),
                RouteStop(route_id=route_b.id, name="Central Library / Block 34", latitude=31.2552, longitude=75.7058, sequence_order=2, estimated_minutes=4),
                RouteStop(route_id=route_b.id, name="Girls Hostels (GH-1 to GH-6)", latitude=31.2515, longitude=75.7075, sequence_order=3, estimated_minutes=8),
                RouteStop(route_id=route_b.id, name="UniMall & Food Court", latitude=31.2529, longitude=75.7048, sequence_order=4, estimated_minutes=12),
            ]
            db.add_all(stops_b)

            # Route C
            route_c = Route(
                name="Campus Perimeter Green Line",
                code="ROUTE-C",
                description="Circumnavigates campus via Unipolis and Sports Complex",
                fare_amount=15.0,
                is_active=True
            )
            db.add(route_c)
            db.flush()

            stops_c = [
                RouteStop(route_id=route_c.id, name="Main Gate (Gate 1)", latitude=31.2538, longitude=75.7012, sequence_order=1, estimated_minutes=0),
                RouteStop(route_id=route_c.id, name="Unipolis & Sports Complex", latitude=31.2530, longitude=75.7025, sequence_order=2, estimated_minutes=4),
                RouteStop(route_id=route_c.id, name="Gate 4 / Residential Area", latitude=31.2510, longitude=75.7005, sequence_order=3, estimated_minutes=8),
                RouteStop(route_id=route_c.id, name="Girls Hostel Area", latitude=31.2515, longitude=75.7075, sequence_order=4, estimated_minutes=13),
            ]
            db.add_all(stops_c)

            # Carts
            cart1 = Cart(cart_number="LPU-CART-01", model="Club Car Transporter 8", total_seats=8, battery_percentage=95, status="ACTIVE", current_route_id=route_a.id, has_cctv=True)
            cart2 = Cart(cart_number="LPU-CART-02", model="Club Car Transporter 8", total_seats=8, battery_percentage=88, status="ACTIVE", current_route_id=route_a.id, has_cctv=True)
            cart3 = Cart(cart_number="LPU-CART-03", model="Club Car Transporter 8", total_seats=8, battery_percentage=75, status="ACTIVE", current_route_id=route_b.id, has_cctv=False)
            cart4 = Cart(cart_number="LPU-CART-04", model="Club Car Transporter 8", total_seats=8, battery_percentage=100, status="CHARGING", current_route_id=route_c.id, has_cctv=True)
            db.add_all([cart1, cart2, cart3, cart4])
            db.flush()

            # Generate 8 seats for each cart
            for c in [cart1, cart2, cart3, cart4]:
                for s in range(1, 9):
                    seat = CartSeat(cart_id=c.id, seat_number=s, seat_label=f"S{s}", is_accessible=(s == 1))
                    db.add(seat)

            # Default Demo Accounts
            # 1. Admin
            admin_user = Profile(
                email="admin@lpu.in",
                full_name="LPU Transport Admin",
                phone_number="+919876543210",
                role="ADMIN",
                hashed_password=get_password_hash("admin123")
            )
            db.add(admin_user)

            # 2. Driver
            driver_user = Profile(
                email="driver@lpu.in",
                full_name="Rajinder Singh",
                phone_number="+919812345678",
                role="DRIVER",
                hashed_password=get_password_hash("driver123")
            )
            db.add(driver_user)
            db.flush()

            driver_ext = Driver(
                id=driver_user.id,
                license_number="DL-PB-09-2021-9988",
                is_available=True,
                assigned_cart_id=cart1.id
            )
            db.add(driver_ext)

            # Create initial active trip for Cart 1
            trip1 = Trip(
                cart_id=cart1.id,
                driver_id=driver_user.id,
                route_id=route_a.id,
                status="IN_TRANSIT"
            )
            db.add(trip1)

            db.commit()
            logger.info("[STARTUP] LPU Database seeded successfully.")
    except Exception as e:
        db.rollback()
        logger.error(f"[STARTUP] Seeding error: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    logger.info("Starting LPU GoCart FastAPI backend engine...")
    init_seed_data()
    yield
    logger.info("Shutting down LPU GoCart API...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Smart Campus E-Cart Booking, Atomic Seat Locking & Real-Time Tracking for Lovely Professional University",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 Routers
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
def root():
    return {
        "app": "LPU GoCart API",
        "campus": "Lovely Professional University (LPU)",
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "OPERATIONAL"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint used by Render and container monitors."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "payment_mode": settings.PAYMENT_MODE
    }

# Real-Time WebSocket Telemetry Endpoint
@app.websocket("/ws/tracking")
async def websocket_tracking_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for live campus telemetry.
    Drivers broadcast continuous coordinates; riders and admin monitors receive live fleet updates.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")
            if msg_type == "DRIVER_LOCATION":
                await ws_manager.broadcast_cart_update(
                    cart_id=data.get("cart_id"),
                    cart_number=data.get("cart_number", "LPU-CART"),
                    latitude=float(data.get("latitude")),
                    longitude=float(data.get("longitude")),
                    speed_kph=float(data.get("speed_kph", 0.0)),
                    heading=data.get("heading"),
                    battery=int(data.get("battery_percentage", 100)),
                    available_seats=int(data.get("available_seats", 8)),
                    route_code=data.get("route_code")
                )
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

