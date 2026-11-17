"""
LPU GoCart - Smart Campus E-Cart Booking & Tracking System
FastAPI Backend Application Entrypoint
Lovely Professional University (LPU), Phagwara, Punjab
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.database.seed import seed_database
from app.api.v1 import api_v1_router
from app.websockets.tracking import ws_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lpu_gocart")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    logger.info("Starting LPU GoCart FastAPI backend engine...")
    seed_database()
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
                    cart_number=data.get("cart_number", "LPU-GC"),
                    latitude=float(data.get("latitude")),
                    longitude=float(data.get("longitude")),
                    speed_kph=float(data.get("speed_kph", 0.0)),
                    heading=data.get("heading"),
                    battery=int(data.get("battery_percentage", 100)),
                    available_seats=int(data.get("available_seats", 6)),
                    route_code=data.get("route_code")
                )
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
