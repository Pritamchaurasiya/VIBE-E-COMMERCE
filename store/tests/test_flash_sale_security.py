from django.test import TestCase, override_settings
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.core.cache import cache
from rest_framework.settings import api_settings
from store.models import FlashSale, Product, Category, Vendor

@override_settings(
    REST_FRAMEWORK={
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle',
            'rest_framework.throttling.ScopedRateThrottle',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '1/minute',
            'user': '1/minute',
            'flash_sales': '1/minute',
        },
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.SessionAuthentication',
        ],
    },
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class FlashSaleSecurityTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=100.00,
            category=self.category,
            vendor=self.vendor
        )

        self.flash_sale = FlashSale.objects.create(
            name='Test Sale',
            slug='test-sale',
            discount_percentage=10,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            is_active=True
        )
        self.flash_sale.products.add(self.product)

    def test_settings_applied(self):
        print(f"Throttle Rates: {api_settings.DEFAULT_THROTTLE_RATES}")

    def test_flash_sale_active_rate_limiting_enforced(self):
        """Test rate limiting on function-based view (using custom decorator)."""
        url = reverse('api_active_flash_sales')

        # 1st request
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # 30 requests should be allowed (limit is 30/min in code, override doesn't affect custom decorator)
        for _ in range(30):
            self.client.get(url)

        # 31st request should fail
        response = self.client.get(url)
        print(f"Function View Status after limit: {response.status_code}")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
