from django.test import TestCase, override_settings
from django.urls import reverse
from store.models import Coupon, User, Product, CartItem, Category, Vendor
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from django.core.cache import cache

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class CouponSecurityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        # Create a coupon
        self.coupon = Coupon.objects.create(
            code='TEST50',
            discount_type='percent',
            discount_value=50,
            min_order_value=1000,  # Minimum order of 1000 required
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            is_active=True
        )

        # Create category and vendor needed for product
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            email='vendor@test.com',
            phone='1234567890'
        )

        # Create a product
        self.product = Product.objects.create(
            name='Test Product',
            price=2000.0,
            stock_quantity=10,
            is_active=True,
            slug='test-product',
            category=self.category,
            vendor=self.vendor
        )

        self.url = '/api/v1/apply-coupon/'

    def test_coupon_bypass_prevented(self):
        """
        Test that providing a fake cart_total does not bypass server-side calculation.
        """
        # User has an empty cart
        # But they send cart_total=2000 in the request

        data = {
            'code': 'TEST50',
            'cart_total': 2000  # Fake total
        }

        request = self.client.post(self.url, data, format='json')

        # Should fail because actual cart total is 0
        self.assertEqual(request.status_code, 200)
        self.assertFalse(request.data['success'])
        self.assertIn('Minimum order value', request.data['error'])

    def test_coupon_valid_cart(self):
        """
        Test that coupon works with a valid cart.
        """
        # Add item to cart
        CartItem.objects.create(
            cart_id=str(self.user.id),
            product=self.product,
            quantity=1
        )

        data = {
            'code': 'TEST50'
        }

        request = self.client.post(self.url, data, format='json')

        self.assertEqual(request.status_code, 200)
        self.assertTrue(request.data['success'])
        self.assertEqual(request.data['discount_amount'], 1000.0) # 50% of 2000
