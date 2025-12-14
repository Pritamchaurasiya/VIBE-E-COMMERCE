"""
Payment Service for VIBE E-Commerce
Handles payment processing, verification, and refunds.
Supports multiple payment gateways including Stripe and Razorpay.
"""
import logging
import hashlib
import hmac
from decimal import Decimal
from typing import Dict, Optional, Tuple
from enum import Enum

from django.conf import settings

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    """Payment status values."""
    PENDING = 'pending'
    PROCESSING = 'processing'
    SUCCESS = 'success'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    PARTIALLY_REFUNDED = 'partially_refunded'
    CANCELLED = 'cancelled'


class PaymentMethod(Enum):
    """Available payment methods."""
    COD = 'cod'
    CREDIT_CARD = 'credit_card'
    DEBIT_CARD = 'debit_card'
    UPI = 'upi'
    NET_BANKING = 'net_banking'
    WALLET = 'wallet'
    RAZORPAY = 'razorpay'
    STRIPE = 'stripe'


class PaymentService:
    """
    Service for handling payment operations.
    """

    def __init__(self):
        self.stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
        self.razorpay_key = getattr(settings, 'RAZORPAY_KEY_ID', None)
        self.razorpay_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)

    def _get_model(self, model_name: str):
        """Lazy import to avoid circular imports."""
        # pylint: disable=import-outside-toplevel
        from store.models import Order
        models_map = {
            'Order': Order,
        }
        return models_map.get(model_name)

    def create_payment_intent(
        self,
        order,
        payment_method: PaymentMethod,
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        Create a payment intent for an order.

        Args:
            order: The order to create payment for
            payment_method: The payment method

        Returns:
            Tuple of (success, message, payment_data)
        """
        try:
            if payment_method == PaymentMethod.STRIPE:
                return self._create_stripe_intent(order)
            elif payment_method == PaymentMethod.RAZORPAY:
                return self._create_razorpay_order(order)
            elif payment_method == PaymentMethod.COD:
                return self._process_cod_order(order)
            else:
                return False, 'Payment method not supported', None

        except Exception as e:
            logger.error("Payment intent creation failed: %s", e)
            return False, str(e), None

    def _create_stripe_intent(self, order) -> Tuple[bool, str, Optional[Dict]]:
        """Create Stripe payment intent."""
        if not self.stripe_key:
            return False, 'Stripe is not configured', None

        try:
            # pylint: disable=import-outside-toplevel
            import stripe
            stripe.api_key = self.stripe_key

            # Convert to cents/paise
            amount = int(order.paid_amount * 100)

            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='inr',
                metadata={
                    'order_id': str(order.id),
                    'order_number': order.order_number,
                },
            )

            return True, 'Payment intent created', {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
            }

        except ImportError:
            return False, 'Stripe library not installed', None
        except Exception as e:
            logger.error("Stripe error: %s", e)
            return False, str(e), None

    def _create_razorpay_order(self, order) -> Tuple[bool, str, Optional[Dict]]:
        """Create Razorpay order."""
        if not self.razorpay_key or not self.razorpay_secret:
            return False, 'Razorpay is not configured', None

        try:
            # pylint: disable=import-outside-toplevel
            import razorpay
            client = razorpay.Client(
                auth=(self.razorpay_key, self.razorpay_secret)
            )

            # Convert to paise
            amount = int(order.paid_amount * 100)

            razorpay_order = client.order.create({
                'amount': amount,
                'currency': 'INR',
                'receipt': order.order_number,
                'notes': {
                    'order_id': str(order.id),
                },
            })

            return True, 'Razorpay order created', {
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key': self.razorpay_key,
                'amount': amount,
            }

        except ImportError:
            return False, 'Razorpay library not installed', None
        except Exception as e:
            logger.error("Razorpay error: %s", e)
            return False, str(e), None

    def _process_cod_order(self, order) -> Tuple[bool, str, Optional[Dict]]:
        """Process Cash on Delivery order."""
        order.payment_method = 'cod'
        order.status = 'confirmed'
        order.save()

        return True, 'COD order confirmed', {
            'payment_method': 'cod',
            'status': 'confirmed',
        }

    def verify_payment(
        self,
        payment_method: PaymentMethod,
        payment_data: Dict,
    ) -> Tuple[bool, str]:
        """
        Verify payment from gateway.

        Args:
            payment_method: The payment method used
            payment_data: Payment verification data

        Returns:
            Tuple of (success, message)
        """
        if payment_method == PaymentMethod.STRIPE:
            return self._verify_stripe_payment(payment_data)
        elif payment_method == PaymentMethod.RAZORPAY:
            return self._verify_razorpay_payment(payment_data)
        else:
            return False, 'Payment method not supported for verification'

    def _verify_stripe_payment(self, payment_data: Dict) -> Tuple[bool, str]:
        """Verify Stripe payment."""
        payment_intent_id = payment_data.get('payment_intent_id')

        if not payment_intent_id:
            return False, 'Payment intent ID required'

        try:
            # pylint: disable=import-outside-toplevel
            import stripe
            stripe.api_key = self.stripe_key

            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if intent.status == 'succeeded':
                return True, 'Payment verified successfully'
            else:
                return False, f'Payment status: {intent.status}'

        except Exception as e:
            logger.error("Stripe verification error: %s", e)
            return False, str(e)

    def _verify_razorpay_payment(self, payment_data: Dict) -> Tuple[bool, str]:
        """Verify Razorpay payment signature."""
        order_id = payment_data.get('razorpay_order_id')
        payment_id = payment_data.get('razorpay_payment_id')
        signature = payment_data.get('razorpay_signature')

        if not all([order_id, payment_id, signature]):
            return False, 'Missing payment verification data'

        try:
            # Verify signature
            message = f'{order_id}|{payment_id}'
            generated_signature = hmac.new(
                self.razorpay_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            if generated_signature == signature:
                return True, 'Payment verified successfully'
            else:
                return False, 'Invalid payment signature'

        except Exception as e:
            logger.error("Razorpay verification error: %s", e)
            return False, str(e)

    def process_refund(
        self,
        order,
        amount: Optional[Decimal] = None,
        reason: str = '',
    ) -> Tuple[bool, str]:
        """
        Process refund for an order.

        Args:
            order: The order to refund
            amount: Refund amount (None for full refund)
            reason: Refund reason

        Returns:
            Tuple of (success, message)
        """
        refund_amount = amount or order.paid_amount

        if refund_amount > order.paid_amount:
            return False, 'Refund amount exceeds order amount'

        try:
            payment_method = getattr(order, 'payment_method', 'cod')

            if payment_method in ['stripe', 'credit_card', 'debit_card']:
                return self._process_stripe_refund(order, refund_amount, reason)
            elif payment_method == 'razorpay':
                return self._process_razorpay_refund(order, refund_amount, reason)
            else:
                # For COD, just mark as refunded
                order.status = 'refunded'
                order.save()
                return True, 'Refund marked for processing'

        except Exception as e:
            logger.error("Refund processing error: %s", e)
            return False, str(e)

    def _process_stripe_refund(
        self,
        order,
        amount: Decimal,
        reason: str
    ) -> Tuple[bool, str]:
        """Process Stripe refund."""
        try:
            # pylint: disable=import-outside-toplevel
            import stripe
            stripe.api_key = self.stripe_key

            payment_intent_id = getattr(order, 'payment_intent_id', None)
            if not payment_intent_id:
                return False, 'No payment intent found for this order'

            refund = stripe.Refund.create(
                payment_intent=payment_intent_id,
                amount=int(amount * 100),
                reason='requested_by_customer',
                metadata={'reason': reason},
            )

            if refund.status == 'succeeded':
                order.status = 'refunded'
                order.save()
                return True, 'Refund processed successfully'
            else:
                return False, f'Refund status: {refund.status}'

        except Exception as e:
            logger.error("Stripe refund error: %s", e)
            return False, str(e)

    def _process_razorpay_refund(
        self,
        order,
        amount: Decimal,
        reason: str
    ) -> Tuple[bool, str]:
        """Process Razorpay refund."""
        try:
            # pylint: disable=import-outside-toplevel
            import razorpay
            client = razorpay.Client(
                auth=(self.razorpay_key, self.razorpay_secret)
            )

            payment_id = getattr(order, 'razorpay_payment_id', None)
            if not payment_id:
                return False, 'No Razorpay payment found for this order'

            refund = client.payment.refund(payment_id, {
                'amount': int(amount * 100),
                'notes': {'reason': reason},
            })

            if refund.get('id'):
                order.status = 'refunded'
                order.save()
                return True, 'Refund processed successfully'
            else:
                return False, 'Refund failed'

        except Exception as e:
            logger.error("Razorpay refund error: %s", e)
            return False, str(e)

    def get_payment_methods(self) -> list:
        """Get available payment methods."""
        methods = [
            {
                'id': 'cod',
                'name': 'Cash on Delivery',
                'icon': '💵',
                'available': True,
            },
            {
                'id': 'upi',
                'name': 'UPI',
                'icon': '📱',
                'available': True,
            },
        ]

        if self.stripe_key:
            methods.append({
                'id': 'stripe',
                'name': 'Credit/Debit Card',
                'icon': '💳',
                'available': True,
            })

        if self.razorpay_key:
            methods.append({
                'id': 'razorpay',
                'name': 'Razorpay',
                'icon': '🔐',
                'available': True,
            })

        return methods
