"""
Order Service for VIBE E-Commerce
Handles order creation, status updates, and order-related operations.
"""
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import uuid

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from .notifications import OrderNotificationHelper

logger = logging.getLogger(__name__)


class OrderService:
    """
    Service for managing order operations.
    """

    ORDER_STATUSES = [
        'pending',
        'confirmed',
        'processing',
        'shipped',
        'out_for_delivery',
        'delivered',
        'cancelled',
        'refunded',
    ]

    def __init__(self, user: User):
        self.user = user
        self.notification_helper = OrderNotificationHelper()

    def _get_model(self, model_name: str):
        """Lazy import to avoid circular imports."""
        # pylint: disable=import-outside-toplevel
        from store.models import Order, OrderItem, Product
        models_map = {
            'Order': Order,
            'OrderItem': OrderItem,
            'Product': Product,
        }
        return models_map.get(model_name)

    def create_order(
        self,
        cart_items: List[Dict],
        shipping_address: Dict,
        billing_address: Optional[Dict] = None,
        payment_method: str = 'cod',
        notes: str = '',
    ) -> Tuple[bool, str, Optional[object]]:
        """
        Create a new order from cart items.

        Args:
            cart_items: List of cart item dictionaries
            shipping_address: Shipping address dictionary
            billing_address: Billing address (optional, defaults to shipping)
            payment_method: Payment method ('cod', 'online', 'wallet')
            notes: Order notes

        Returns:
            Tuple of (success, message, order object or None)
        """
        if not cart_items:
            return False, 'Cart is empty', None

        # pylint: disable=invalid-name
        order_model = self._get_model('Order')
        order_item_model = self._get_model('OrderItem')
        product_model = self._get_model('Product')

        try:
            with transaction.atomic():
                # Calculate totals
                subtotal = Decimal('0.00')
                items_data = []

                for cart_item in cart_items:
                    product_id = cart_item.get('product_id')
                    quantity = cart_item.get('quantity', 1)

                    # pylint: disable=no-member
                    product = product_model.objects.select_for_update().get(
                        id=product_id,
                        is_active=True
                    )

                    # Validate stock
                    if hasattr(product, 'stock') and product.stock < quantity:
                        return (
                            False,
                            f'Insufficient stock for {product.name}',
                            None
                        )

                    item_total = product.price * quantity
                    subtotal += item_total

                    items_data.append({
                        'product': product,
                        'quantity': quantity,
                        'price': product.price,
                        'total': item_total,
                    })

                # Calculate shipping
                shipping = Decimal('50.00') if subtotal < Decimal('500.00') else Decimal('0.00')
                total = subtotal + shipping

                # Create order
                # pylint: disable=no-member
                order = order_model.objects.create(
                    user=self.user,
                    order_number=self._generate_order_number(),
                    status='pending',
                    subtotal=subtotal,
                    shipping_cost=shipping,
                    paid_amount=total,
                    payment_method=payment_method,
                    shipping_name=shipping_address.get('name', ''),
                    shipping_address=shipping_address.get('address', ''),
                    shipping_city=shipping_address.get('city', ''),
                    shipping_state=shipping_address.get('state', ''),
                    shipping_pincode=shipping_address.get('pincode', ''),
                    shipping_phone=shipping_address.get('phone', ''),
                    notes=notes,
                )

                # Create order items and update stock
                for item_data in items_data:
                    # pylint: disable=no-member
                    order_item_model.objects.create(
                        order=order,
                        product=item_data['product'],
                        vendor=item_data['product'].vendor,
                        quantity=item_data['quantity'],
                        price=item_data['price'],
                    )

                    # Update stock
                    product = item_data['product']
                    if hasattr(product, 'stock'):
                        product.stock -= item_data['quantity']
                        product.save(update_fields=['stock'])

                # Send notification
                self.notification_helper.notify_order_placed(order)

                logger.info(
                    "Order %s created for user %s",
                    order.order_number, self.user.id
                )

                return True, 'Order created successfully', order

        except product_model.DoesNotExist:
            return False, 'One or more products not found', None
        except (ValueError, TypeError) as e:
            logger.error("Order creation error: %s", e)
            return False, 'Error creating order', None

    def _generate_order_number(self) -> str:
        """Generate a unique order number."""
        timestamp = timezone.now().strftime('%Y%m%d%H%M')
        unique_id = uuid.uuid4().hex[:6].upper()
        return f'ORD-{timestamp}-{unique_id}'

    def get_order(self, order_id: int) -> Optional[object]:
        """Get an order by ID."""
        # pylint: disable=invalid-name
        order_model = self._get_model('Order')

        try:
            # pylint: disable=no-member
            return order_model.objects.get(id=order_id, user=self.user)
        except order_model.DoesNotExist:
            return None

    def get_order_by_number(self, order_number: str) -> Optional[object]:
        """Get an order by order number."""
        # pylint: disable=invalid-name
        order_model = self._get_model('Order')

        try:
            # pylint: disable=no-member
            return order_model.objects.get(
                order_number=order_number,
                user=self.user
            )
        except order_model.DoesNotExist:
            return None

    def get_user_orders(
        self,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[object]:
        """Get orders for the current user."""
        # pylint: disable=invalid-name
        order_model = self._get_model('Order')

        # pylint: disable=no-member
        queryset = order_model.objects.filter(user=self.user)

        if status:
            queryset = queryset.filter(status=status)

        return list(queryset.order_by('-created_at')[:limit])

    def update_order_status(
        self,
        order_id: int,
        new_status: str,
        tracking_number: str = ''
    ) -> Tuple[bool, str]:
        """
        Update order status.

        Args:
            order_id: Order ID
            new_status: New status
            tracking_number: Tracking number (for shipped orders)

        Returns:
            Tuple of (success, message)
        """
        if new_status not in self.ORDER_STATUSES:
            return False, f'Invalid status: {new_status}'

        order = self.get_order(order_id)
        if not order:
            return False, 'Order not found'

        old_status = order.status
        order.status = new_status

        if tracking_number:
            order.tracking_number = tracking_number

        order.save()

        # Send appropriate notification
        if new_status == 'confirmed' and old_status == 'pending':
            self.notification_helper.notify_order_confirmed(order)
        elif new_status == 'shipped':
            self.notification_helper.notify_order_shipped(order, tracking_number)
        elif new_status == 'delivered':
            self.notification_helper.notify_order_delivered(order)
        elif new_status == 'cancelled':
            self.notification_helper.notify_order_cancelled(order)

        logger.info(
            "Order %s status updated: %s -> %s",
            order.order_number, old_status, new_status
        )

        return True, f'Order status updated to {new_status}'

    def cancel_order(
        self,
        order_id: int,
        reason: str = ''
    ) -> Tuple[bool, str]:
        """
        Cancel an order.

        Args:
            order_id: Order ID
            reason: Cancellation reason

        Returns:
            Tuple of (success, message)
        """
        order = self.get_order(order_id)
        if not order:
            return False, 'Order not found'

        # Can only cancel pending or confirmed orders
        if order.status not in ['pending', 'confirmed']:
            return False, f'Cannot cancel order with status: {order.status}'

        order.status = 'cancelled'
        order.cancelled_at = timezone.now()
        order.cancellation_reason = reason
        order.save()

        # Restore stock
        # pylint: disable=invalid-name
        order_item_model = self._get_model('OrderItem')
        # pylint: disable=no-member
        order_items = order_item_model.objects.filter(order=order)

        for item in order_items:
            product = item.product
            if hasattr(product, 'stock'):
                product.stock += item.quantity
                product.save(update_fields=['stock'])

        # Send notification
        self.notification_helper.notify_order_cancelled(order, reason)

        logger.info("Order %s cancelled", order.order_number)

        return True, 'Order cancelled successfully'

    def get_order_tracking(self, order_id: int) -> Optional[Dict]:
        """Get order tracking information."""
        order = self.get_order(order_id)
        if not order:
            return None

        tracking_steps = [
            {
                'status': 'pending',
                'label': 'Order Placed',
                'completed': order.status != 'pending' or order.status == 'pending',
                'timestamp': order.created_at.isoformat() if order.created_at else None,
            },
            {
                'status': 'confirmed',
                'label': 'Order Confirmed',
                'completed': order.status in [
                    'confirmed', 'processing', 'shipped',
                    'out_for_delivery', 'delivered'
                ],
                'timestamp': None,
            },
            {
                'status': 'shipped',
                'label': 'Shipped',
                'completed': order.status in [
                    'shipped', 'out_for_delivery', 'delivered'
                ],
                'timestamp': None,
            },
            {
                'status': 'out_for_delivery',
                'label': 'Out for Delivery',
                'completed': order.status in ['out_for_delivery', 'delivered'],
                'timestamp': None,
            },
            {
                'status': 'delivered',
                'label': 'Delivered',
                'completed': order.status == 'delivered',
                'timestamp': None,
            },
        ]

        return {
            'order_number': order.order_number,
            'current_status': order.status,
            'tracking_number': getattr(order, 'tracking_number', ''),
            'steps': tracking_steps,
        }


class OrderAnalytics:
    """
    Analytics for order data.
    """

    def __init__(self, user: Optional[User] = None):
        self.user = user

    def _get_model(self, model_name: str):
        """Lazy import to avoid circular imports."""
        # pylint: disable=import-outside-toplevel
        from store.models import Order, OrderItem
        models_map = {
            'Order': Order,
            'OrderItem': OrderItem,
        }
        return models_map.get(model_name)

    def get_user_stats(self) -> Dict:
        """Get order statistics for the current user."""
        if not self.user:
            return {}

        # pylint: disable=invalid-name
        order_model = self._get_model('Order')

        # pylint: disable=no-member
        orders = order_model.objects.filter(user=self.user)

        total_orders = orders.count()
        total_spent = sum(
            o.paid_amount for o in orders.filter(status='delivered')
        )

        return {
            'total_orders': total_orders,
            'total_spent': str(total_spent),
            'pending_orders': orders.filter(status='pending').count(),
            'delivered_orders': orders.filter(status='delivered').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
        }
