"""
LPU GoCart - QR Code Boarding Validation Service
Verifies digital QR tickets scanned by drivers using smartphone camera.
"""

from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.database.models.models import QRTicket, Booking, Driver, CartSeat, Profile

def verify_and_redeem_ticket(
    db: Session,
    qr_token: str,
    driver_id: str
) -> Dict[str, Any]:
    """
    Verify student QR code ticket scanned by the cart driver.
    Marks ticket as used and booking as BOARDED.
    """
    # 1. Lookup ticket by token or booking code
    ticket = db.query(QRTicket).filter(QRTicket.qr_token == qr_token).first()
    
    if not ticket and qr_token.startswith("LPU-TICKET:"):
        parts = qr_token.split(":")
        if len(parts) >= 2:
            booking_code = parts[1]
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

    # 2. Check if already boarded
    if ticket.is_used or booking.status == "BOARDED":
        return {
            "valid": False,
            "message": f"Ticket already used on {ticket.scanned_at.strftime('%H:%M:%S') if ticket.scanned_at else 'earlier'}.",
            "booking_code": booking.booking_code
        }

    if booking.status != "CONFIRMED":
        return {
            "valid": False,
            "message": f"Ticket cannot be boarded. Current status is {booking.status}."
        }

    # 3. Mark as boarded
    now = datetime.now(timezone.utc)
    ticket.is_used = True
    ticket.scanned_at = now
    ticket.scanned_by_driver_id = driver_id
    booking.status = "BOARDED"

    db.commit()

    student_name = booking.student.profile.full_name if booking.student and booking.student.profile else "Student"
    seat_label = booking.seat.seat_label if booking.seat else f"Seat #{booking.seat_id}"

    return {
        "valid": True,
        "message": f"Boarding Verified! Welcome aboard, {student_name}.",
        "booking_code": booking.booking_code,
        "student_name": student_name,
        "seat_label": seat_label,
        "scanned_at": now.isoformat()
    }

