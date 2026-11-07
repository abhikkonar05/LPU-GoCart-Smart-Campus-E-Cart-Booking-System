"""
LPU GoCart - Payment Gateway Schemas (Demo & Razorpay)
"""

from typing import Optional
from pydantic import BaseModel

class PaymentIntentRequest(BaseModel):
    booking_id: str
    amount: float
    gateway: str = "demo" # "demo" or "razorpay"

class PaymentIntentResponse(BaseModel):
    payment_id: str
    booking_id: str
    amount: float
    currency: str = "INR"
    gateway: str
    gateway_order_id: Optional[str] = None
    razorpay_key_id: Optional[str] = None
    status: str

class DemoPaymentConfirmRequest(BaseModel):
    payment_id: str
    booking_id: str
    simulate_status: str = "SUCCESS" # "SUCCESS" or "FAILURE"

class PaymentResultResponse(BaseModel):
    success: bool
    payment_id: str
    booking_id: str
    booking_status: str
    transaction_reference: str
    message: str

