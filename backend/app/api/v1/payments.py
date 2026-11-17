"""
LPU GoCart - Payment REST Router
Handles checkout intents and payment confirmation with the pluggable gateway.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Payment, Booking, User
from app.schemas.payment import (
    PaymentIntentRequest, PaymentIntentResponse,
    DemoPaymentConfirmRequest, PaymentResultResponse
)
from app.gateways.payments.factory import get_payment_gateway
from app.services.booking_service import confirm_booking_payment
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create-intent", response_model=PaymentIntentResponse)
def create_payment_intent(
    req: PaymentIntentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initialize payment intent for a booking.
    Delegates to Demo or Razorpay gateway based on system configuration.
    """
    booking = db.query(Booking).filter(Booking.id == req.booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

    if booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    gateway = get_payment_gateway()
    order_data = gateway.create_order(
        booking_id=booking.id,
        amount=req.amount,
        currency="INR"
    )

    # Persist or update Payment record
    payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if not payment:
        payment = Payment(
            booking_id=booking.id,
            user_id=current_user.id,
            amount=req.amount,
            currency="INR",
            gateway=order_data["gateway"],
            gateway_order_id=order_data["order_id"],
            status="PENDING"
        )
        db.add(payment)
    else:
        payment.gateway_order_id = order_data["order_id"]
        payment.gateway = order_data["gateway"]
        payment.amount = req.amount

    db.commit()
    db.refresh(payment)

    return PaymentIntentResponse(
        payment_id=payment.id,
        booking_id=booking.id,
        amount=payment.amount,
        currency="INR",
        gateway=payment.gateway,
        gateway_order_id=payment.gateway_order_id,
        razorpay_key_id=order_data.get("razorpay_key_id"),
        status=payment.status
    )

@router.post("/demo-confirm", response_model=PaymentResultResponse)
def confirm_demo_payment(
    req: DemoPaymentConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process simulated demo payment.
    The backend verifies the simulation and triggers booking confirmation idempotently.
    """
    payment = db.query(Payment).filter(Payment.id == req.payment_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found.")

    gateway = get_payment_gateway()
    verification = gateway.verify_payment({"simulate_status": req.simulate_status})

    now = datetime.now(timezone.utc)
    if verification["success"]:
        payment.status = "COMPLETED"
        payment.gateway_payment_id = verification["transaction_id"]
        payment.completed_at = now
        
        # Confirm booking and issue QR ticket
        confirm_booking_payment(db, req.booking_id, verification["transaction_id"])
        db.commit()

        return PaymentResultResponse(
            success=True,
            payment_id=payment.id,
            booking_id=payment.booking_id,
            booking_status="CONFIRMED",
            transaction_reference=verification["transaction_id"],
            message="Payment successful! Boarding pass issued."
        )
    else:
        payment.status = "FAILED"
        payment.completed_at = now
        db.commit()

        return PaymentResultResponse(
            success=False,
            payment_id=payment.id,
            booking_id=payment.booking_id,
            booking_status="PENDING",
            transaction_reference="FAILED",
            message=verification.get("message", "Simulated payment failed.")
        )
