"""
LPU GoCart - Demo Payment Gateway Implementation
Provides instant, zero-cost simulated transactions for local development, testing,
and campus demonstrations without requiring real credit cards or external bank accounts.
"""

import uuid
from typing import Dict, Any
from app.gateways.payments.base import BasePaymentGateway

class DemoPaymentGateway(BasePaymentGateway):
    """Zero-cost local demo payment gateway."""

    def create_order(self, booking_id: str, amount: float, currency: str = "INR") -> Dict[str, Any]:
        """Generate a simulated demo order."""
        order_id = f"demo_ord_{uuid.uuid4().hex[:12]}"
        return {
            "gateway": "demo",
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "status": "CREATED",
            "message": "Demo payment order initialized. Simulating instant verification."
        }

    def verify_payment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify demo payment result.
        Accepts simulate_status ('SUCCESS' or 'FAILURE').
        """
        simulate_status = payload.get("simulate_status", "SUCCESS").upper()
        
        if simulate_status == "SUCCESS":
            txn_id = f"demo_txn_{uuid.uuid4().hex[:14]}"
            return {
                "success": True,
                "status": "COMPLETED",
                "transaction_id": txn_id,
                "gateway": "demo",
                "message": "Demo payment simulated successfully."
            }
        else:
            return {
                "success": False,
                "status": "FAILED",
                "transaction_id": None,
                "gateway": "demo",
                "message": payload.get("error_reason", "Simulated payment failure by user.")
            }

    def refund_payment(self, payment_id: str, amount: float) -> Dict[str, Any]:
        """Simulate refund."""
        return {
            "success": True,
            "status": "REFUNDED",
            "refund_id": f"demo_rf_{uuid.uuid4().hex[:10]}",
            "amount": amount
        }

