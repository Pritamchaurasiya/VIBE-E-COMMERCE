"""
Cart Service for VIBE E-Commerce
Enhanced cart functionality with validation, pricing rules, and promotions.
"""
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from django.contrib.auth.models import User
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CartService:
    """
    Service for managing shopping cart operations.
    """

    SHIPPING_THRESHOLD = Decimal('500.00')  # Free shipping above this amount
    SHIPPING_CHARGE = Decimal('50.00')
    MAX_QUANTITY_PER_ITEM = 100

    def __init__(self, session=None, user: Optional[User] = None):
        self.session = session
        self.user = user
        self._cart = None

    def _get_model(self, model_name: str):
        """Lazy import to avoid circular imports."""
        # pylint: disable=import-outside-toplevel
        from store.models import Product, Coupon
        models_map = {
            'Product': Product,
            'Coupon': Coupon,
        }
        return models_map.get(model_name)

    def _get_cart_key(self) -> str:
        """Get the cache key for the cart."""
        if self.user and self.user.is_authenticated:
            return f'cart_user_{self.user.id}'
        return f'cart_session_{self.session.session_key}'

    def get_cart(self) -> Dict:
        """Get the current cart contents."""
        if self._cart is None:
            cart_key = self._get_cart_key()
            self._cart = cache.get(cart_key, {'items': {}, 'coupon': None})
        return self._cart

    def _save_cart(self):
        """Save the cart to cache."""
        cart_key = self._get_cart_key()
        cache.set(cart_key, self._cart, 86400)  # 24 hour expiry

    def add_item(
        self,
        product_id: int,
        quantity: int = 1,
        update_quantity: bool = False
    ) -> Tuple[bool, str]:
        """
        Add an item to the cart.

        Args:
            product_id: ID of the product to add
            quantity: Quantity to add
            update_quantity: If True, set quantity; if False, increment

        Returns:
            Tuple of (success, message)
        """
        # pylint: disable=invalid-name
        product_model = self._get_model('Product')

        try:
            # pylint: disable=no-member
            product = product_model.objects.get(id=product_id, is_active=True)
        except product_model.DoesNotExist:
            return False, 'Product not found'

        # Validate quantity
        if quantity < 1:
            return False, 'Quantity must be at least 1'

        if quantity > self.MAX_QUANTITY_PER_ITEM:
            return False, f'Maximum quantity is {self.MAX_QUANTITY_PER_ITEM}'

        # Check stock
        if hasattr(product, 'stock') and product.stock < quantity:
            return False, f'Only {product.stock} items available'

        cart = self.get_cart()
        product_key = str(product_id)

        if update_quantity:
            cart['items'][product_key] = {
                'product_id': product_id,
                'quantity': quantity,
                'price': str(product.price),
                'name': product.name,
            }
        else:
            if product_key in cart['items']:
                new_qty = cart['items'][product_key]['quantity'] + quantity
                if new_qty > self.MAX_QUANTITY_PER_ITEM:
                    return False, f'Cannot add more. Max is {self.MAX_QUANTITY_PER_ITEM}'
                cart['items'][product_key]['quantity'] = new_qty
            else:
                cart['items'][product_key] = {
                    'product_id': product_id,
                    'quantity': quantity,
                    'price': str(product.price),
                    'name': product.name,
                }

        self._save_cart()
        return True, 'Item added to cart'

    def remove_item(self, product_id: int) -> Tuple[bool, str]:
        """Remove an item from the cart."""
        cart = self.get_cart()
        product_key = str(product_id)

        if product_key in cart['items']:
            del cart['items'][product_key]
            self._save_cart()
            return True, 'Item removed from cart'

        return False, 'Item not in cart'

    def update_quantity(
        self,
        product_id: int,
        quantity: int
    ) -> Tuple[bool, str]:
        """Update quantity of an item in the cart."""
        if quantity < 1:
            return self.remove_item(product_id)

        return self.add_item(product_id, quantity, update_quantity=True)

    def clear(self):
        """Clear the cart."""
        self._cart = {'items': {}, 'coupon': None}
        self._save_cart()

    def get_item_count(self) -> int:
        """Get total number of items in cart."""
        cart = self.get_cart()
        return sum(item['quantity'] for item in cart['items'].values())

    def get_subtotal(self) -> Decimal:
        """Calculate cart subtotal."""
        cart = self.get_cart()
        subtotal = Decimal('0.00')

        for item in cart['items'].values():
            subtotal += Decimal(item['price']) * item['quantity']

        return subtotal

    def apply_coupon(self, coupon_code: str) -> Tuple[bool, str]:
        """Apply a coupon code to the cart."""
        # pylint: disable=invalid-name
        coupon_model = self._get_model('Coupon')

        try:
            # pylint: disable=no-member
            coupon = coupon_model.objects.get(
                code__iexact=coupon_code,
                is_active=True
            )
        except coupon_model.DoesNotExist:
            return False, 'Invalid coupon code'

        # Check minimum order amount
        subtotal = self.get_subtotal()
        if hasattr(coupon, 'min_order_amount') and subtotal < coupon.min_order_amount:
            return False, f'Minimum order amount is ₹{coupon.min_order_amount}'

        # Check usage limit
        if hasattr(coupon, 'usage_limit') and coupon.usage_limit:
            if hasattr(coupon, 'times_used') and coupon.times_used >= coupon.usage_limit:
                return False, 'Coupon usage limit reached'

        cart = self.get_cart()
        cart['coupon'] = {
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': str(coupon.discount_value),
        }
        self._save_cart()

        return True, f'Coupon {coupon.code} applied!'

    def remove_coupon(self):
        """Remove applied coupon."""
        cart = self.get_cart()
        cart['coupon'] = None
        self._save_cart()

    def get_discount(self) -> Decimal:
        """Calculate discount amount."""
        cart = self.get_cart()

        if not cart.get('coupon'):
            return Decimal('0.00')

        coupon = cart['coupon']
        subtotal = self.get_subtotal()

        if coupon['discount_type'] == 'percentage':
            discount = subtotal * (Decimal(coupon['discount_value']) / 100)
        else:  # fixed amount
            discount = Decimal(coupon['discount_value'])

        # Discount cannot exceed subtotal
        return min(discount, subtotal)

    def get_shipping(self) -> Decimal:
        """Calculate shipping charge."""
        subtotal = self.get_subtotal()

        if subtotal >= self.SHIPPING_THRESHOLD:
            return Decimal('0.00')

        return self.SHIPPING_CHARGE

    def get_total(self) -> Decimal:
        """Calculate cart total."""
        subtotal = self.get_subtotal()
        discount = self.get_discount()
        shipping = self.get_shipping()

        return subtotal - discount + shipping

    def get_cart_summary(self) -> Dict:
        """Get a complete cart summary."""
        cart = self.get_cart()

        return {
            'items': list(cart['items'].values()),
            'item_count': self.get_item_count(),
            'subtotal': str(self.get_subtotal()),
            'discount': str(self.get_discount()),
            'shipping': str(self.get_shipping()),
            'total': str(self.get_total()),
            'coupon': cart.get('coupon'),
            'free_shipping_threshold': str(self.SHIPPING_THRESHOLD),
        }

    def validate_cart_for_checkout(self) -> Tuple[bool, List[str]]:
        """
        Validate cart before checkout.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        cart = self.get_cart()

        if not cart['items']:
            errors.append('Cart is empty')
            return False, errors

        # pylint: disable=invalid-name
        product_model = self._get_model('Product')

        for product_key, item in cart['items'].items():
            try:
                # pylint: disable=no-member
                product = product_model.objects.get(id=item['product_id'])

                # Check if still active
                if not product.is_active:
                    errors.append(f'{item["name"]} is no longer available')

                # Check stock
                if hasattr(product, 'stock') and product.stock < item['quantity']:
                    errors.append(
                        f'{item["name"]}: Only {product.stock} available'
                    )

                # Check price change
                if Decimal(item['price']) != product.price:
                    errors.append(
                        f'{item["name"]}: Price has changed to ₹{product.price}'
                    )
                    # Update cart with new price
                    cart['items'][product_key]['price'] = str(product.price)

            except product_model.DoesNotExist:
                errors.append(f'{item["name"]} is no longer available')
                del cart['items'][product_key]

        if errors:
            self._save_cart()
            return False, errors

        return True, []

    def merge_carts(self, session_cart_key: str):
        """
        Merge session cart into user cart after login.

        Args:
            session_cart_key: The session key of the anonymous cart
        """
        if not self.user or not self.user.is_authenticated:
            return

        session_cart = cache.get(f'cart_session_{session_cart_key}', {})

        if not session_cart or not session_cart.get('items'):
            return

        user_cart = self.get_cart()

        # Merge items
        for product_key, item in session_cart.get('items', {}).items():
            if product_key in user_cart['items']:
                # Add quantities
                user_cart['items'][product_key]['quantity'] += item['quantity']
            else:
                user_cart['items'][product_key] = item

        # Clear session cart
        cache.delete(f'cart_session_{session_cart_key}')

        self._save_cart()
        logger.info(
            "Merged session cart into user %s cart", self.user.id
        )
