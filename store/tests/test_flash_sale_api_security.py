from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from store.models import FlashSale, Product, Category, Vendor
from rest_framework import status
from rest_framework.test import APIClient

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        },
        'session': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-session',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.cache'
)
class FlashSaleSecurityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product', slug='test-product', price=100.00,
            category=self.category, vendor=self.vendor
        )

        self.flash_sale = FlashSale.objects.create(
            name='Test Sale',
            slug='test-sale',
            discount_percentage=10,
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1),
            is_active=True
        )
        self.flash_sale.products.add(self.product)

    def test_get_active_flash_sales(self):
        url = reverse('api_active_flash_sales')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_get_flash_sale_detail(self):
        url = reverse('api_flash_sale_detail_v2', args=[self.flash_sale.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_subscribe_flash_sale_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_flash_sale_subscribe', args=[self.flash_sale.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_subscribe_flash_sale_unauthenticated(self):
        url = reverse('api_flash_sale_subscribe', args=[self.flash_sale.id])
        response = self.client.post(url)
        # Should be 403 Forbidden (DRF) or 401
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_unsubscribe_flash_sale(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_flash_sale_unsubscribe', args=[self.flash_sale.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_flash_sale_countdown(self):
        url = reverse('api_flash_sale_countdown', args=[self.flash_sale.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
