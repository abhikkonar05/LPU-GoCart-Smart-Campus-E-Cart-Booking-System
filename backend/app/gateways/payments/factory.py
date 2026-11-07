"""
LPU GoCart - Payment Gateway Factory
Instantiates the configured payment gateway based on environment configuration.
"""

from app.core.config import settings
from app.gateways.payments.base import BasePaymentGateway
from app.gateways.payments.demo import DemoPaymentGateway
from app.gateways.payments.razorpay import RazorpayPaymentGateway

def get_payment_gateway() -> BasePaymentGateway:
    """Return configured payment gateway (Demo or Razorpay)."""
    mode = (settings.PAYMENT_MODE or "demo").lower()
    if mode == "razorpay":
        return RazorpayPaymentGateway()
    return DemoPaymentGateway()

