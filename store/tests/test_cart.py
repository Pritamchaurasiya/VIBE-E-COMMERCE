"""
Cart test module for VIBE E-Commerce.

Tests for cart functionality including adding, updating, and removing products.
"""
# pylint: disable=no-member
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User, AnonymousUser
from store.models import Product, Category, Vendor
from store.cart import Cart


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class CartTestCase(TestCase):
    """Test cases for Cart functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        # Create a vendor for products (required field)
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Test City'
        )
        self.product1 = Product.objects.create(
            category=self.category,
            vendor=self.vendor,
            name='Test Product 1',
            slug='test-product-1',
            price=10.00
        )
        self.product2 = Product.objects.create(
            category=self.category,
            vendor=self.vendor,
            name='Test Product 2',
            slug='test-product-2',
            price=20.00
        )

    def _get_request_with_session(self, user=None):
        """Create a request with an active session and optional user."""
        request = self.factory.get('/')

        # Add session middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        # Add user to request (anonymous by default)
        request.user = user if user else AnonymousUser()

        return request

    def test_add_to_cart(self):
        """Test adding products to cart."""
        request = self._get_request_with_session()
        cart = Cart(request)

        cart.add(product_id=self.product1.id)
        self.assertEqual(len(cart), 1)

        cart.add(product_id=self.product1.id)
        self.assertEqual(len(cart), 2)

        cart.add(product_id=self.product2.id)
        self.assertEqual(len(cart), 3)

        self.assertEqual(cart.get_total_cost(), 40.00)

    def test_update_cart(self):
        """Test updating cart quantities."""
        request = self._get_request_with_session()
        cart = Cart(request)

        # Add items
        cart.add(product_id=self.product1.id)
        cart.add(product_id=self.product1.id)
        self.assertEqual(len(cart), 2)

        # Update to a specific quantity
        cart.add(product_id=self.product1.id, quantity=5, update_quantity=True)
        self.assertEqual(len(cart), 5)

        # Update to another quantity
        cart.add(product_id=self.product1.id, quantity=3, update_quantity=True)
        self.assertEqual(len(cart), 3)

        # Setting quantity to 0 or negative removes the item
        cart.add(product_id=self.product1.id, quantity=0, update_quantity=True)
        self.assertEqual(len(cart), 0)

    def test_remove_from_cart(self):
        """Test removing products from cart."""
        request = self._get_request_with_session()
        cart = Cart(request)
        cart.add(product_id=self.product1.id)
        self.assertEqual(len(cart), 1)

        cart.remove(product_id=self.product1.id)
        self.assertEqual(len(cart), 0)

    def test_cart_migration(self):
        """Test migration of old cart format to new format."""
        # Simulate old cart data format (integer instead of dict)
        request = self._get_request_with_session()
        session = request.session
        # Use the correct session key 'cart' (from settings.CART_SESSION_ID)
        session['cart'] = {str(self.product1.id): 2}
        session.save()

        cart = Cart(request)
        self.assertEqual(len(cart), 2)
        self.assertEqual(cart.get_total_cost(), 20.00)

        # Check if it has been migrated to the new format
        self.assertIsInstance(cart.cart_data[str(self.product1.id)], dict)
        self.assertEqual(cart.cart_data[str(self.product1.id)]['quantity'], 2)

    def test_authenticated_user_cart(self):
        """Test cart functionality for authenticated users."""
        request = self._get_request_with_session(user=self.user)
        cart = Cart(request)

        cart.add(product_id=self.product1.id)
        self.assertEqual(len(cart), 1)

        cart.add(product_id=self.product1.id, quantity=3, update_quantity=True)
        self.assertEqual(len(cart), 3)

        # Verify the cart persists in DB by creating a new cart instance
        cart2 = Cart(request)
        self.assertEqual(len(cart2), 3)

        cart.clear()
        cart3 = Cart(request)
        self.assertEqual(len(cart3), 0)

    def test_empty_cart(self):
        """Test empty cart properties."""
        request = self._get_request_with_session()
        cart = Cart(request)

        self.assertEqual(len(cart), 0)
        self.assertEqual(cart.get_total_cost(), 0)

    def test_cart_iteration(self):
        """Test cart iteration returns items correctly."""
        request = self._get_request_with_session()
        cart = Cart(request)

        cart.add(product_id=self.product1.id, quantity=2)
        cart.add(product_id=self.product2.id, quantity=3)

        items = list(cart)
        self.assertEqual(len(items), 2)
