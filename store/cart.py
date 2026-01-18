"""
Cart management module.
"""
# pylint: disable=no-member
from django.conf import settings
from .models import Product, CartItem


class Cart:
    """
    Cart class to manage the shopping cart in the session or database.
    """

    def __init__(self, request):
        self.session = request.session
        self.request = request
        self.products_cache = {}
        # Check if user is authenticated (works for Session and Token auth)
        self.user = (
            request.user if request.user and request.user.is_authenticated else None
        )

        if self.user:
            # DB-backed cart for logged-in users
            self.cart_data = {}
            items = CartItem.objects.filter(
                cart_id=str(self.user.id)
            ).select_related('product')
            for item in items:
                pid = str(item.product.id)
                self.cart_data[pid] = {
                    'quantity': item.quantity,
                    'id': pid
                }
                # Pre-populate cache with products fetched via select_related
                self.products_cache[pid] = item.product
        else:
            # Session-backed cart for anonymous users
            cart_session = self.session.get(settings.CART_SESSION_ID)
            if not cart_session:
                cart_session = self.session[settings.CART_SESSION_ID] = {}
            self.cart_data = cart_session

        # Ensure consistency
        if any(not isinstance(value, dict) for value in self.cart_data.values()):
            self.cart_data = {
                key: (
                    {'quantity': value, 'id': key}
                    if not isinstance(value, dict)
                    else value
                )
                for key, value in self.cart_data.items()
            }
            if not self.user:
                self.save()

    def _fetch_products(self):
        """Fetch products that are not yet in the cache."""
        product_ids = list(self.cart_data.keys())
        missing_ids = [pid for pid in product_ids if pid not in self.products_cache]

        if missing_ids:
            products = Product.objects.filter(id__in=missing_ids)
            for product in products:
                self.products_cache[str(product.id)] = product

    def __iter__(self):
        self._fetch_products()

        cart_data_copy = self.cart_data.copy()

        for pid, item in cart_data_copy.items():
            product = self.products_cache.get(pid)
            if product:
                item['product'] = product
                item['price'] = self._calculate_unit_price(
                    product, item['quantity']
                )
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart_data.values())

    def save(self):
        """
        Mark the session as modified or save to DB.
        """
        if self.user:
            # DB Save
            current_ids = [int(pid) for pid in self.cart_data.keys()]

            # Remove items not in cart anymore
            CartItem.objects.filter(
                cart_id=str(self.user.id)
            ).exclude(product__id__in=current_ids).delete()

            # Update/Create items
            for product_id, item_data in self.cart_data.items():
                CartItem.objects.update_or_create(
                    cart_id=str(self.user.id),
                    product_id=product_id,
                    defaults={'quantity': item_data['quantity']}
                )
        else:
            # Session Save
            self.session[settings.CART_SESSION_ID] = self.cart_data
            self.session.modified = True

    def add(self, product_id, quantity=1, update_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product_id)

        if product_id not in self.cart_data:
            self.cart_data[product_id] = {'quantity': 0, 'id': product_id}

        if update_quantity:
            self.cart_data[product_id]['quantity'] = int(quantity)
        else:
            self.cart_data[product_id]['quantity'] += int(quantity)

        if self.cart_data[product_id]['quantity'] <= 0:
            self.remove(product_id)
        else:
            self.save()

    def remove(self, product_id):
        """
        Remove a product from the cart.
        """
        product_id = str(product_id)
        if product_id in self.cart_data:
            del self.cart_data[product_id]
            # Also remove from cache if present
            if product_id in self.products_cache:
                del self.products_cache[product_id]
            self.save()

    def clear(self):
        """
        Remove the cart from the session or DB.
        """
        if self.user:
            CartItem.objects.filter(cart_id=str(self.user.id)).delete()
            self.cart_data = {}
        else:
            del self.session[settings.CART_SESSION_ID]
            self.session.modified = True
        self.products_cache = {}

    def _calculate_unit_price(self, product, quantity):
        """
        Calculate unit price based on quantity (Bulk Pricing).
        """
        has_bulk = (
            product.bulk_price and
            product.bulk_min_quantity and
            quantity >= product.bulk_min_quantity
        )
        if has_bulk:
            return product.bulk_price
        return product.price

    def get_total_cost(self):
        """
        Calculate the total cost of items in the cart.
        """
        self._fetch_products()
        total = 0
        for pid, item in self.cart_data.items():
            product = self.products_cache.get(pid)
            if product:
                quantity = item['quantity']
                unit_price = self._calculate_unit_price(product, quantity)
                total += unit_price * quantity
        return total
