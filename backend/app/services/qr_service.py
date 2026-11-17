"""
LPU GoCart - QR Code Boarding Validation Service
Verifies digital QR tickets scanned by drivers using camera or manual code entry.
"""

from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.database.models import QRTicket, Booking, User, CartSeat

def verify_and_redeem_ticket(
    db: Session,
    qr_token: str,
    driver_id: str
) -> Dict[str, Any]:
    """
    Verify passenger QR code ticket scanned by the cart driver.
    Marks ticket as verified and booking as CHECKED_IN.
    """
    clean_token = qr_token.strip()
    # 1. Lookup ticket by token or booking code
    ticket = db.query(QRTicket).filter(QRTicket.qr_token == clean_token).first()
    
    if not ticket and (clean_token.startswith("LPU-TICKET:") or clean_token.startswith("LPU-BK-")):
        booking_code = clean_token.split(":")[-1]
        booking = db.query(Booking).filter(Booking.booking_code == booking_code).first()
        if booking:
            ticket = db.query(QRTicket).filter(QRTicket.booking_id == booking.id).first()

    if not ticket:
        return {
            "valid": False,
            "message": "Invalid QR Ticket. No active booking matches this code."
        }

    booking = ticket.booking
    if not booking:
        return {"valid": False, "message": "Booking record missing."}

    # 2. Check if already checked in or boarded
    if ticket.is_verified or booking.status in ("CHECKED_IN", "BOARDED"):
        time_str = ticket.verified_at.strftime('%H:%M:%S') if ticket.verified_at else 'earlier'
        return {
            "valid": False,
            "message": f"Ticket already used and checked in at {time_str}.",
            "booking_code": booking.booking_code
        }

    if booking.status != "CONFIRMED":
        return {
            "valid": False,
            "message": f"Ticket cannot be checked in. Current status is {booking.status}."
        }

    # 3. Mark as checked in
    now = datetime.now(timezone.utc)
    ticket.is_verified = True
    ticket.verified_at = now
    ticket.verified_by_driver_id = driver_id
    booking.status = "CHECKED_IN"

    db.commit()

    passenger_name = booking.user.full_name if booking.user else "Passenger"
    seat_label = booking.seat.seat_label if booking.seat else (f"Full Cart" if booking.booking_type == "FULL_CART" else "General")

    return {
        "valid": True,
        "message": f"Boarding Verified! Welcome aboard, {passenger_name}.",
        "booking_code": booking.booking_code,
        "passenger_name": passenger_name,
        "seat_label": seat_label,
        "booking_type": booking.booking_type,
        "scanned_at": now.isoformat()
    }
