"""
LPU GoCart - Live GPS Telemetry Service
Caches latest cart locations in-memory for low-latency retrieval
and logs telemetry points to PostgreSQL.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models.models import GPSLocation, Cart

# In-memory latest positions: cart_id -> dict
LATEST_CART_POSITIONS: Dict[str, Dict[str, Any]] = {}

def record_gps_telemetry(
    db: Session,
    cart_id: str,
    driver_id: str,
    latitude: float,
    longitude: float,
    speed_kph: float = 0.0,
    heading: Optional[float] = None,
    accuracy_meters: Optional[float] = None,
    trip_id: Optional[str] = None
) -> Dict[str, Any]:
    """Log GPS position update and update in-memory cache."""
    now = datetime.now(timezone.utc)
    
    # 1. Update in-memory telemetry cache
    payload = {
        "cart_id": cart_id,
        "driver_id": driver_id,
        "trip_id": trip_id,
        "latitude": latitude,
        "longitude": longitude,
        "speed_kph": speed_kph,
        "heading": heading,
        "accuracy_meters": accuracy_meters,
        "timestamp": now.isoformat()
    }
    LATEST_CART_POSITIONS[cart_id] = payload

    # 2. Persist to database
    location = GPSLocation(
        cart_id=cart_id,
        driver_id=driver_id,
        trip_id=trip_id,
        latitude=latitude,
        longitude=longitude,
        speed_kph=speed_kph,
        heading=heading,
        accuracy_meters=accuracy_meters,
        recorded_at=now
    )
    db.add(location)
    db.commit()
    return payload

def get_latest_cart_position(cart_id: str) -> Optional[Dict[str, Any]]:
    """Fetch latest known coordinates for a cart."""
    return LATEST_CART_POSITIONS.get(cart_id)

def get_all_active_cart_positions() -> Dict[str, Dict[str, Any]]:
    """Return latest coordinates for all operating carts."""
    return LATEST_CART_POSITIONS

