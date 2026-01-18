
import json
from decimal import Decimal
from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from store.models import Coupon, Product, Category, Vendor
from django.utils import timezone
from datetime import timedelta

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'session': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    AXES_ENABLED=False
)
class CouponSecurityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=100.00,
            category=self.category,
            vendor=self.vendor,
            stock_quantity=10
        )

        self.coupon = Coupon.objects.create(
            code='SAVE50',
            discount_type='percent',
            discount_value=10,
            min_order_value=500.00,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            is_active=True
        )

    def test_apply_coupon_bypass_vulnerability(self):
        """
        Test that a user CANNOT bypass minimum order value by sending a fake cart_total.
        """
        # Ensure cart is empty
        session = self.client.session
        session['cart'] = {}
        session.save()

        # Try to apply coupon with fake high total
        url = reverse('api_apply_coupon')
        data = {
            'code': 'SAVE50',
            'cart_total': 1000  # Fake total > min_order_value
        }

        response = self.client.post(url, data, content_type='application/json')

        # If vulnerable, it returns 200 OK with success=True
        # We want it to fail because the actual cart is empty (0)

        self.assertEqual(response.status_code, 200)
        json_response = response.json()

        # Success should be False because server-side total is 0 (empty cart),
        # even though we sent cart_total=1000.
        self.assertFalse(json_response.get('success'), "Server should reject coupon when actual cart total is low")
        self.assertIn('Minimum order value', json_response.get('error', ''))
