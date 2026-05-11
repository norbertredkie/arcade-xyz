"""
Stripe payment integration for credit pack purchases
"""

import os
import logging
import stripe
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StripePaymentHandler:
    """Handle Stripe payments for credit pack purchases."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Stripe client."""
        key = api_key or os.getenv("STRIPE_SECRET_KEY")
        if not key:
            raise ValueError("STRIPE_SECRET_KEY not configured")
        stripe.api_key = key

    def create_payment_intent(
        self, user_id: str, amount_cents: int, pack_amount: int, metadata: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe PaymentIntent for credit pack purchase.
        
        Args:
            user_id: Arcade.XYZ user ID
            amount_cents: Price in cents (e.g., 999 for $9.99)
            pack_amount: Number of credits in pack
            metadata: Additional metadata to attach
            
        Returns:
            Payment intent dict with client_secret
        """
        try:
            meta = metadata or {}
            meta.update({
                "user_id": user_id,
                "pack_amount": str(pack_amount),
                "service": "arcade-xyz-credits",
            })

            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                metadata=meta,
                description=f"Arcade.XYZ Credit Pack - {pack_amount} credits",
            )

            logger.info(
                f"💳 Payment intent created: {intent.id} | "
                f"{user_id} | ${amount_cents/100:.2f}"
            )

            return {
                "intent_id": intent.id,
                "client_secret": intent.client_secret,
                "amount": intent.amount,
                "currency": intent.currency,
                "status": intent.status,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating intent: {e}")
            raise

    def confirm_payment(self, intent_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Confirm a payment intent (retrieve current status).
        
        Returns: (success, message, intent_data)
        """
        try:
            intent = stripe.PaymentIntent.retrieve(intent_id)

            if intent.status == "succeeded":
                logger.info(f"✅ Payment confirmed: {intent_id}")
                return True, "Payment successful", {
                    "intent_id": intent.id,
                    "status": intent.status,
                    "amount": intent.amount,
                    "charge_id": intent.charges.data[0].id if intent.charges.data else None,
                }

            elif intent.status == "processing":
                return False, "Payment is processing, check back soon", {
                    "intent_id": intent.id,
                    "status": intent.status,
                }

            elif intent.status == "requires_payment_method":
                return False, "Payment method required", {
                    "intent_id": intent.id,
                    "status": intent.status,
                }

            else:
                return False, f"Payment failed with status: {intent.status}", {
                    "intent_id": intent.id,
                    "status": intent.status,
                }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error confirming payment: {e}")
            return False, f"Error: {str(e)}", {}

    def refund_payment(self, charge_id: str, reason: str = "requested_by_customer") -> Tuple[bool, str]:
        """
        Refund a completed payment.
        
        Args:
            charge_id: Stripe charge ID
            reason: Refund reason
            
        Returns: (success, message)
        """
        try:
            refund = stripe.Refund.create(
                charge=charge_id,
                reason=reason,
            )

            logger.info(f"↩️ Refund created: {refund.id} | Charge: {charge_id}")
            return True, f"Refund processed: {refund.id}"

        except stripe.error.StripeError as e:
            logger.error(f"Stripe refund error: {e}")
            return False, f"Refund failed: {str(e)}"

    def verify_webhook_signature(self, body: str, sig_header: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify and parse a Stripe webhook.
        
        Returns: (valid, event_dict)
        """
        try:
            endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
            if not endpoint_secret:
                logger.warning("STRIPE_WEBHOOK_SECRET not configured")
                return False, {}

            event = stripe.Webhook.construct_event(
                body,
                sig_header,
                endpoint_secret,
            )

            logger.info(f"✅ Webhook verified: {event['type']}")
            return True, event

        except ValueError as e:
            logger.error(f"Invalid webhook body: {e}")
            return False, {}
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False, {}

    def handle_payment_succeeded_webhook(self, intent_id: str, metadata: Dict[str, str]) -> Dict[str, Any]:
        """
        Process a payment_intent.succeeded webhook event.
        
        Returns: dict with details for credit system to process
        """
        try:
            intent = stripe.PaymentIntent.retrieve(intent_id)

            return {
                "success": True,
                "intent_id": intent_id,
                "user_id": metadata.get("user_id"),
                "pack_amount": int(metadata.get("pack_amount", 0)),
                "amount": intent.amount,
                "currency": intent.currency,
                "charge_id": intent.charges.data[0].id if intent.charges.data else None,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def get_payment_history(self, user_id: str, limit: int = 10) -> list:
        """Get payment history for a user (by metadata)."""
        try:
            intents = stripe.PaymentIntent.list(
                limit=limit,
                metadata={"user_id": user_id},
            )

            return [
                {
                    "intent_id": intent.id,
                    "amount": intent.amount,
                    "currency": intent.currency,
                    "status": intent.status,
                    "created": intent.created,
                    "pack_amount": intent.metadata.get("pack_amount"),
                }
                for intent in intents.data
            ]

        except stripe.error.StripeError as e:
            logger.error(f"Error fetching payment history: {e}")
            return []
