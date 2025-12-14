"""
Testing utilities and base classes for the store app.

This module provides common test fixtures, helper methods,
and base test classes for consistent testing patterns.

Note: Snyk may report "Use of Hardcoded Credentials" warnings for test fixture
usernames in login helper methods. These are expected false positives - test
usernames are not security-sensitive. Passwords use environment variables.

Snyk/Bandit Suppressions: nosec B105, nosec B106 - All credentials in this
file are intentionally hardcoded for isolated test environments only.

Pylint: no-member warnings on Django model .objects are false positives.
"""
# pylint: disable=no-member
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase, Client
# django.urls.reverse available if needed in subclasses

# Import centralized test credentials
from store.tests.test_config import (
    TEST_USER_PASSWORD,
    TEST_ADMIN_PASSWORD,
    TEST_USERNAME,
    TEST_ADMIN_USERNAME,
)


class BaseTestCase(TestCase):
    """Base test case with common fixtures and helper methods."""

    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase."""
        # pylint: disable=import-outside-toplevel
        from store.models import Category, Vendor, Product

        # Create categories
        cls.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        # Create test user
        cls.user = User.objects.create_user(
            username=TEST_USERNAME,
            email='testuser@example.com',
            password=TEST_USER_PASSWORD
        )

        # Create admin user
        cls.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )

        # Create vendor
        cls.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Test City',
            created_by=cls.admin_user
        )

        # Create products
        cls.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='A test product description',
            price=Decimal('99.99'),
            stock_quantity=100,
            category=cls.category,
            vendor=cls.vendor
        )

    def setUp(self):
        """Set up for each test method."""
        self.client = Client()

    def login_user(self):
        """Login as regular user."""
        # nosec B106 - Test credentials for isolated test environment
        self.client.login(
            username=TEST_USERNAME,
            password=TEST_USER_PASSWORD
        )  # noqa: S106  # nosec B106

    def login_admin(self):
        """Login as admin user."""
        # nosec B106 - Test credentials for isolated test environment
        self.client.login(
            username=TEST_ADMIN_USERNAME,
            password=TEST_ADMIN_PASSWORD
        )  # noqa: S106  # nosec B106

    def get_json_response(self, url, **kwargs):
        """Make GET request expecting JSON response."""
        response = self.client.get(url, **kwargs)
        if response.content:
            try:
                return response.json()
            except ValueError:
                return None
        return None

    def post_json(self, url, data=None, **kwargs):
        """Make POST request with JSON data."""
        return self.client.post(
            url,
            data=data,
            content_type='application/json',
            **kwargs
        )


class AuthenticatedTestCase(BaseTestCase):
    """Test case that starts with user logged in."""

    def setUp(self):
        """Set up with logged in user."""
        super().setUp()
        self.login_user()


class AdminTestCase(BaseTestCase):
    """Test case that starts with admin logged in."""

    def setUp(self):
        """Set up with logged in admin."""
        super().setUp()
        self.login_admin()


class APITestMixin:
    """Mixin for API testing utilities."""

    def get_api_client(self):
        """Get an API client with proper headers."""
        # pylint: disable=import-outside-toplevel
        from rest_framework.test import APIClient
        return APIClient()

    def authenticate_api_client(self, client, user=None):
        """Authenticate API client with token."""
        # pylint: disable=import-outside-toplevel
        from rest_framework.authtoken.models import Token
        user = user or self.user
        token, _ = Token.objects.get_or_create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        return client

    def assert_api_success(self, response):
        """Assert API response indicates success."""
        self.assertIn(
            response.status_code,
            [200, 201, 204],
            f"Expected success status, got {response.status_code}"
        )

    def assert_api_error(self, response, expected_status=None):
        """Assert API response indicates error."""
        if expected_status:
            self.assertEqual(response.status_code, expected_status)
        else:
            self.assertIn(
                response.status_code,
                [400, 401, 403, 404, 500],
                f"Expected error status, got {response.status_code}"
            )


class CartTestMixin:
    """Mixin for cart-related testing utilities."""

    def add_to_cart(self, product, quantity=1):
        """Add product to cart via API."""
        # pylint: disable=import-outside-toplevel
        from store.cart import Cart
        session = self.client.session
        cart = Cart(self.client)
        cart.add(product, quantity)
        session.save()

    def get_cart_count(self):
        """Get number of items in cart."""
        # pylint: disable=import-outside-toplevel
        from store.cart import Cart
        cart = Cart(self.client)
        return len(cart)

    def clear_cart(self):
        """Clear the cart."""
        # pylint: disable=import-outside-toplevel
        from store.cart import Cart
        cart = Cart(self.client)
        cart.clear()


class OrderTestMixin:
    """Mixin for order-related testing utilities."""

    def create_test_order(self, user=None, products=None, paid=False):
        """Create a test order with items."""
        # pylint: disable=import-outside-toplevel
        from store.models import Order, OrderItem

        user = user or self.user
        products = products or [self.product]

        order = Order.objects.create(
            user=user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            address='123 Test St',
            city='Test City',
            state='Test State',
            postal_code='12345',
            phone='1234567890',
            paid=paid
        )

        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                vendor=product.vendor,
                price=product.price,
                quantity=1
            )

        return order


def create_test_user(username='testuser', email=None, password=None, **extra_fields):
    """Create a test user with reasonable defaults."""
    email = email or f'{username}@example.com'
    password = password or TEST_USER_PASSWORD
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        **extra_fields
    )


def create_test_admin(username='admin', email=None, password=None, **extra_fields):
    """Create a test admin user."""
    email = email or f'{username}@example.com'
    password = password or TEST_ADMIN_PASSWORD
    return User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        **extra_fields
    )


def create_test_product(name='Test Product', price='99.99', stock=100, **kwargs):
    """Create a test product with reasonable defaults."""
    # pylint: disable=import-outside-toplevel
    from store.models import Product, Category, Vendor

    # Get or create category
    category = kwargs.pop('category', None)
    if not category:
        category, _ = Category.objects.get_or_create(
            slug='test-category',
            defaults={'name': 'Test Category'}
        )

    # Get or create vendor
    vendor = kwargs.pop('vendor', None)
    if not vendor:
        vendor = Vendor.objects.first()
        if not vendor:
            admin = User.objects.filter(is_superuser=True).first()
            if not admin:
                admin = create_test_admin()
            vendor = Vendor.objects.create(
                name='Test Vendor',
                slug='test-vendor',
                city='Test City',
                created_by=admin
            )

    # Create unique slug
    base_slug = kwargs.pop('slug', name.lower().replace(' ', '-'))
    slug = base_slug
    counter = 1
    while Product.objects.filter(slug=slug).exists():
        slug = f'{base_slug}-{counter}'
        counter += 1

    return Product.objects.create(
        name=name,
        slug=slug,
        price=Decimal(str(price)),
        stock_quantity=stock,
        category=category,
        vendor=vendor,
        **kwargs
    )
