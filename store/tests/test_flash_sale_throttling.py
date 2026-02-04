import os
import django
from django.conf import settings
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from store.models import FlashSale, Product, Category, Vendor
from django.utils import timezone
from datetime import timedelta

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class FlashSaleApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')

        # Create dummy data
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', email='vendor@test.com')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=100.00,
            stock_quantity=10,
            category=self.category,
            vendor=self.vendor,
            is_active=True
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
        url = '/api/v1/flash-sales/active/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['sales']), 1)

    def test_get_flash_sale_detail(self):
        url = f'/api/v1/flash-sales/{self.flash_sale.id}/detail/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['sale']['id'], self.flash_sale.id)

    def test_subscribe_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = f'/api/v1/flash-sales/{self.flash_sale.id}/subscribe/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_subscribe_unauthenticated(self):
        url = f'/api/v1/flash-sales/{self.flash_sale.id}/subscribe/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unsubscribe_authenticated(self):
        self.client.force_authenticate(user=self.user)
        # Subscribe first
        session = self.client.session
        session['flash_sale_subscriptions'] = [self.flash_sale.id]
        session.save()

        url = f'/api/v1/flash-sales/{self.flash_sale.id}/unsubscribe/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
