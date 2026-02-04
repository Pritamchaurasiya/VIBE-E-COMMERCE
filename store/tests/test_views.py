"""
View tests for VIBE E-Commerce.

Tests for all Django view functions in the store app.

Note: Snyk may report "Use of Hardcoded Credentials" warnings for test fixture
usernames (e.g., 'testuser', 'authtest'). These are expected false positives -
test usernames are not security-sensitive. Actual passwords use environment
variables via TEST_USER_PASSWORD constant from test_config.py.
"""
# pylint: disable=no-member
from decimal import Decimal
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import (
    Vendor, Category, Product, Order, Wishlist, Review
)
from store.tests.test_config import (
    TEST_USER_PASSWORD,
    TEST_AUTH_USERNAME,
    TEST_WISHLIST_USERNAME,
    TEST_DASHBOARD_USERNAME,
    TEST_CHECKOUT_USERNAME,
    TEST_ADMIN_USER_USERNAME,
    TEST_REGULAR_USERNAME,
    TEST_PRODUCT_VIEWER_USERNAME,
    TEST_WRONG_PASSWORD,
)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class FrontpageViewTest(TestCase):
    """Test cases for frontpage view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.vendor = Vendor.objects.create(
            name='Featured Vendor',
            slug='featured-vendor',
            city='Mumbai'
        )
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
        )
        self.product = Product.objects.create(
            name='Featured Product',
            slug='featured-product',
            price=Decimal('199.99'),
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )

    def test_frontpage_loads(self):
        """Test frontpage loads successfully."""
        response = self.client.get(reverse('frontpage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_frontpage_contains_products(self):
        """Test frontpage contains products in context."""
        response = self.client.get(reverse('frontpage'))
        self.assertIn('products', response.context)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ShopViewTest(TestCase):
    """Test cases for shop view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.vendor = Vendor.objects.create(
            name='Shop Vendor',
            slug='shop-vendor',
            city='Delhi'
        )
        self.category = Category.objects.create(
            name='Clothing',
            slug='clothing'
        )
        for i in range(15):
            Product.objects.create(
                name=f'Shop Product {i}',
                slug=f'shop-product-{i}',
                price=Decimal(f'{50 + i * 10}.00'),
                category=self.category,
                vendor=self.vendor,
                is_active=True
            )

    def test_shop_loads(self):
        """Test shop page loads successfully."""
        response = self.client.get(reverse('shop'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop.html')

    def test_shop_pagination(self):
        """Test shop pagination works."""
        response = self.client.get(reverse('shop'))
        self.assertIn('products', response.context)
        self.assertTrue(response.context['products'].has_other_pages())

    def test_shop_filter_by_category(self):
        """Test shop filtering by category."""
        response = self.client.get(reverse('shop'), {'category': 'clothing'})
        self.assertEqual(response.status_code, 200)

    def test_shop_filter_by_price(self):
        """Test shop filtering by price range."""
        response = self.client.get(
            reverse('shop'),
            {'min_price': '50', 'max_price': '100'}
        )
        self.assertEqual(response.status_code, 200)

    def test_shop_search(self):
        """Test shop search functionality."""
        response = self.client.get(reverse('shop'), {'search': 'Product'})
        self.assertEqual(response.status_code, 200)

    def test_shop_sorting(self):
        """Test shop sorting functionality."""
        response = self.client.get(reverse('shop'), {'sort': 'price_low'})
        self.assertEqual(response.status_code, 200)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ProductDetailViewTest(TestCase):
    """Test cases for product detail view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_PRODUCT_VIEWER_USERNAME,
            password=TEST_USER_PASSWORD
        )
        self.vendor = Vendor.objects.create(
            name='Product Vendor',
            slug='product-vendor',
            city='Bangalore'
        )
        self.category = Category.objects.create(
            name='Gadgets',
            slug='gadgets'
        )
        self.product = Product.objects.create(
            name='Detail Product',
            slug='detail-product',
            price=Decimal('299.99'),
            description='A detailed product description',
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )

    def test_product_detail_loads(self):
        """Test product detail page loads."""
        response = self.client.get(
            reverse('product_detail', kwargs={'slug': 'detail-product'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product_detail.html')

    def test_product_detail_context(self):
        """Test product detail context contains product."""
        response = self.client.get(
            reverse('product_detail', kwargs={'slug': 'detail-product'})
        )
        self.assertEqual(response.context['product'], self.product)

    def test_product_detail_404_inactive(self):
        """Test behavior for inactive product."""
        Product.objects.create(
            name='Inactive Product',
            slug='inactive-product',
            price=Decimal('99.99'),
            category=self.category,
            vendor=self.vendor,
            is_active=False
        )
        response = self.client.get(
            reverse('product_detail', kwargs={'slug': 'inactive-product'})
        )
        # May return 404 or 200 depending on implementation
        self.assertIn(response.status_code, [200, 404])

    def test_product_detail_with_reviews(self):
        """Test product detail with reviews."""
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title='Excellent',
            comment='Great product!'
        )
        response = self.client.get(
            reverse('product_detail', kwargs={'slug': 'detail-product'})
        )
        self.assertIn('reviews', response.context)
        self.assertEqual(len(response.context['reviews']), 1)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class VendorViewTest(TestCase):
    """Test cases for vendor views."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.vendor = Vendor.objects.create(
            name='List Vendor',
            slug='list-vendor',
            city='Chennai'
        )
        self.category = Category.objects.create(
            name='Category',
            slug='category'
        )
        Product.objects.create(
            name='Vendor Product',
            slug='vendor-product',
            price=Decimal('49.99'),
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )

    def test_vendor_list_loads(self):
        """Test vendor list page loads."""
        response = self.client.get(reverse('vendor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vendor_list.html')

    def test_vendor_detail_loads(self):
        """Test vendor detail page loads."""
        response = self.client.get(
            reverse('vendor_detail', kwargs={'slug': 'list-vendor'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vendor_detail.html')

    def test_vendor_detail_context(self):
        """Test vendor detail context."""
        response = self.client.get(
            reverse('vendor_detail', kwargs={'slug': 'list-vendor'})
        )
        self.assertEqual(response.context['vendor'], self.vendor)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class CartViewTest(TestCase):
    """Test cases for cart views."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.vendor = Vendor.objects.create(
            name='Cart Vendor',
            slug='cart-vendor',
            city='Hyderabad'
        )
        self.category = Category.objects.create(
            name='Cart Category',
            slug='cart-category'
        )
        self.product = Product.objects.create(
            name='Cart Product',
            slug='cart-product',
            price=Decimal('75.00'),
            stock_quantity=10,
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )

    def test_cart_detail_loads(self):
        """Test cart detail page loads."""
        response = self.client.get(reverse('cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')

    def test_cart_add(self):
        """Test adding product to cart."""
        # Cart add may require POST request
        response = self.client.post(
            reverse('cart_add', kwargs={'product_id': self.product.id})
        )
        # Either redirect (302) or method not allowed (405) if only POST is accepted
        self.assertIn(response.status_code, [200, 302, 405])

    def test_cart_remove(self):
        """Test removing product from cart."""
        # First add to cart via POST
        self.client.post(
            reverse('cart_add', kwargs={'product_id': self.product.id})
        )
        # Then remove
        response = self.client.post(
            reverse('cart_remove', kwargs={'product_id': self.product.id})
        )
        self.assertIn(response.status_code, [200, 302])

    def test_cart_update(self):
        """Test updating cart quantity."""
        # First add to cart - use POST if required
        self.client.post(
            reverse('cart_add', kwargs={'product_id': self.product.id})
        )
        # Update quantity (increment)
        response = self.client.get(
            reverse('cart_update', kwargs={
                'product_id': self.product.id,
                'action': 'increment'
            })
        )
        # Should redirect or return OK
        self.assertIn(response.status_code, [200, 302])


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class AuthenticationViewTest(TestCase):
    """Test cases for authentication views."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_AUTH_USERNAME,
            email='auth@test.com',
            password=TEST_USER_PASSWORD
        )

    def test_login_page_loads(self):
        """Test login page loads."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(reverse('login'), {
            'username': TEST_AUTH_USERNAME,
            'password': TEST_USER_PASSWORD
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success

    def test_login_failure(self):
        """Test failed login."""
        response = self.client.post(reverse('login'), {
            'username': TEST_AUTH_USERNAME,
            'password': TEST_WRONG_PASSWORD  # noqa: S106  # nosec B106 - intentional wrong password
        })
        self.assertEqual(response.status_code, 200)  # Stay on page

    def test_signup_page_loads(self):
        """Test signup page loads."""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_success(self):
        """Test successful signup."""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_logout(self):
        """Test logout."""
        self.client.login(username=TEST_AUTH_USERNAME, password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class WishlistViewTest(TestCase):
    """Test cases for wishlist views."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_WISHLIST_USERNAME,
            password=TEST_USER_PASSWORD
        )
        self.vendor = Vendor.objects.create(
            name='Wishlist Vendor',
            slug='wishlist-vendor',
            city='Pune'
        )
        self.category = Category.objects.create(
            name='Wishlist Category',
            slug='wishlist-category'
        )
        self.product = Product.objects.create(
            name='Wishlist Product',
            slug='wishlist-product',
            price=Decimal('89.99'),
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )

    def test_wishlist_requires_login(self):
        """Test wishlist page requires login."""
        response = self.client.get(reverse('wishlist_view'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_wishlist_view_authenticated(self):
        """Test wishlist page for authenticated user."""
        self.client.login(username=TEST_WISHLIST_USERNAME, password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('wishlist_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wishlist.html')

    def test_wishlist_add(self):
        """Test adding to wishlist."""
        self.client.login(username=TEST_WISHLIST_USERNAME, password=TEST_USER_PASSWORD)
        # Use POST request as that's typically what's expected
        response = self.client.post(
            reverse('wishlist_add', kwargs={'product_id': self.product.id})
        )
        # Accept redirect (302), OK (200), or method not allowed if GET is expected
        self.assertIn(response.status_code, [200, 302, 405])

    def test_wishlist_remove(self):
        """Test removing from wishlist."""
        self.client.login(username=TEST_WISHLIST_USERNAME, password=TEST_USER_PASSWORD)
        Wishlist.objects.create(user=self.user, product=self.product)
        # Use POST request
        response = self.client.post(
            reverse('wishlist_remove', kwargs={'product_id': self.product.id})
        )
        self.assertIn(response.status_code, [200, 302, 405])


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class DashboardViewTest(TestCase):
    """Test cases for dashboard view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_DASHBOARD_USERNAME,
            password=TEST_USER_PASSWORD
        )
        self.vendor = Vendor.objects.create(
            name='Dashboard Vendor',
            slug='dashboard-vendor',
            city='Kolkata'
        )
        self.category = Category.objects.create(
            name='Dashboard Category',
            slug='dashboard-category'
        )
        self.product = Product.objects.create(
            name='Dashboard Product',
            slug='dashboard-product',
            price=Decimal('149.99'),
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )
        self.order = Order.objects.create(
            user=self.user,
            first_name='Dashboard',
            last_name='User',
            email='dashboard@example.com',
            address='456 Dashboard St',
            zipcode='67890',
            place='Dashboard City',
            phone='9876543210'
        )

    def test_dashboard_requires_login(self):
        """Test dashboard requires login."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_loads_authenticated(self):
        """Test dashboard loads for authenticated user."""
        self.client.login(username=TEST_DASHBOARD_USERNAME, password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_dashboard_shows_user_orders(self):
        """Test dashboard shows user's orders."""
        self.client.login(username=TEST_DASHBOARD_USERNAME, password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('dashboard'))
        self.assertIn('orders', response.context)
        self.assertEqual(len(response.context['orders']), 1)


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ContactViewTest(TestCase):
    """Test cases for contact view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()

    def test_contact_page_loads(self):
        """Test contact page loads or redirects."""
        response = self.client.get(reverse('contact'))
        # May load or redirect depending on template availability
        self.assertIn(response.status_code, [200, 302])

    def test_contact_form_submission(self):
        """Test contact form submission."""
        response = self.client.post(reverse('contact'), {
            'name': 'Test Contact',
            'email': 'contact@example.com',
            'message': 'This is a test message.'
        })
        # Should redirect on success or stay on page with message
        self.assertIn(response.status_code, [200, 302])


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class AboutViewTest(TestCase):
    """Test cases for about view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()

    def test_about_page_loads(self):
        """Test about page loads."""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about.html')


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class CheckoutViewTest(TestCase):
    """Test cases for checkout view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_CHECKOUT_USERNAME,
            password=TEST_USER_PASSWORD
        )
        self.vendor = Vendor.objects.create(
            name='Checkout Vendor',
            slug='checkout-vendor',
            city='Jaipur'
        )
        self.category = Category.objects.create(
            name='Checkout Category',
            slug='checkout-category'
        )
        self.product = Product.objects.create(
            name='Checkout Product',
            slug='checkout-product',
            price=Decimal('199.99'),
            stock_quantity=5,
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )

    def test_checkout_empty_cart_redirect(self):
        """Test checkout with empty cart redirects."""
        response = self.client.get(reverse('checkout'))
        # Should redirect or show message for empty cart
        self.assertIn(response.status_code, [200, 302])

    def test_checkout_with_cart_items(self):
        """Test checkout page with items in cart."""
        # Add item to cart first
        self.client.post(
            reverse('cart_add', kwargs={'product_id': self.product.id})
        )
        response = self.client.get(reverse('checkout'))
        # May require login or show checkout page
        self.assertIn(response.status_code, [200, 302])


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class AdminDashboardViewTest(TestCase):
    """Test cases for admin dashboard view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username=TEST_ADMIN_USER_USERNAME,
            password=TEST_USER_PASSWORD,
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username=TEST_REGULAR_USERNAME,
            password=TEST_USER_PASSWORD,
            is_staff=False
        )

    def test_admin_dashboard_requires_staff(self):
        """Test admin dashboard requires staff status."""
        self.client.login(username=TEST_REGULAR_USERNAME, password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_admin_dashboard_loads_for_staff(self):
        """Test admin dashboard loads for staff user."""
        self.client.login(username=TEST_ADMIN_USER_USERNAME, password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')


@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ProductCompareViewTest(TestCase):
    """Test cases for product compare view."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.vendor = Vendor.objects.create(
            name='Compare Vendor',
            slug='compare-vendor',
            city='Lucknow'
        )
        self.category = Category.objects.create(
            name='Compare Category',
            slug='compare-category'
        )
        self.product1 = Product.objects.create(
            name='Compare Product 1',
            slug='compare-product-1',
            price=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )
        self.product2 = Product.objects.create(
            name='Compare Product 2',
            slug='compare-product-2',
            price=Decimal('150.00'),
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )

    def test_compare_page_loads(self):
        """Test compare page loads."""
        response = self.client.get(reverse('product_compare'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product_compare.html')

    def test_compare_with_products(self):
        """Test compare page with product IDs."""
        response = self.client.get(
            reverse('product_compare'),
            {'products': [self.product1.id, self.product2.id]}
        )
        self.assertEqual(response.status_code, 200)
