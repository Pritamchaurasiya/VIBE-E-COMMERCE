import json
from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from store.models import FlashSale
from store.flash_sale_api import get_active_flash_sales, get_flash_sale_detail

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake-security',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class FlashSaleSecurityTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')
        cache.clear()

        # Create a mock flash sale
        self.sale = FlashSale.objects.create(
            name='Test Sale',
            slug='test-sale',
            discount_percentage=10,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            is_active=True
        )

    def test_rate_limit_active_sales(self):
        """Test rate limiting for get_active_flash_sales (60/min)."""
        limit = 60
        url = '/api/v1/flash-sales/active/'

        # Should pass 'limit' times
        for _ in range(limit):
            request = self.factory.get(url)
            request.user = self.user
            response = get_active_flash_sales(request)
            self.assertEqual(response.status_code, 200)

        # Should fail on next attempt
        request = self.factory.get(url)
        request.user = self.user
        response = get_active_flash_sales(request)
        self.assertEqual(response.status_code, 429)

        # Verify JSON content
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Too many requests')

    def test_rate_limit_detail_view(self):
        """Test rate limiting for get_flash_sale_detail (60/min)."""
        limit = 60
        url = f'/api/v1/flash-sales/{self.sale.id}/detail/'

        # Should pass 'limit' times
        for _ in range(limit):
            request = self.factory.get(url)
            request.user = self.user
            response = get_flash_sale_detail(request, self.sale.id)
            self.assertEqual(response.status_code, 200)

        # Should fail on next attempt
        request = self.factory.get(url)
        request.user = self.user
        response = get_flash_sale_detail(request, self.sale.id)
        self.assertEqual(response.status_code, 429)
