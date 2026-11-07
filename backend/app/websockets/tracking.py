"""
LPU GoCart - Real-Time WebSocket Telemetry Gateway
Broadcasts live cart locations from driver smartphones to students and admin monitors.
"""

from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger("lpu_gocart.websockets")

class TrackingConnectionManager:
    """Manages active WebSocket connections for live fleet map streaming."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast payload to all subscribed students and admin consoles."""
        text_data = json.dumps(message)
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(text_data)
            except Exception:
                disconnected.append(connection)
        
        # Clean up stale connections
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_cart_update(
        self,
        cart_id: str,
        cart_number: str,
        latitude: float,
        longitude: float,
        speed_kph: float = 0.0,
        heading: float = None,
        battery: int = 100,
        available_seats: int = 8,
        route_code: str = None
    ):
        """Standardized cart location broadcast."""
        payload = {
            "event": "CART_UPDATE",
            "cart_id": cart_id,
            "cart_number": cart_number,
            "latitude": latitude,
            "longitude": longitude,
            "speed_kph": speed_kph,
            "heading": heading,
            "battery_percentage": battery,
            "available_seats": available_seats,
            "route_code": route_code,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await self.broadcast(payload)

ws_manager = TrackingConnectionManager()

