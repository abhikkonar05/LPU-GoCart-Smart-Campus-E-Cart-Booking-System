"""
LPU GoCart - Abstract Base Payment Gateway Interface
Defines the contract that both Demo and Razorpay gateways must adhere to.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BasePaymentGateway(ABC):
    """Abstract interface for student fare payment processing."""

    @abstractmethod
    def create_order(self, booking_id: str, amount: float, currency: str = "INR") -> Dict[str, Any]:
        """Create a payment intent or order with the provider."""
        pass

    @abstractmethod
    def verify_payment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verify provider signature, callback, or simulated payment result."""
        pass

    @abstractmethod
    def refund_payment(self, payment_id: str, amount: float) -> Dict[str, Any]:
        """Initiate refund in case of cancellation or dispute."""
        pass

