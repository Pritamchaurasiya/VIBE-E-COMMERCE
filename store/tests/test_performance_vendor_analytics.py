from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Vendor, Product, Order, OrderItem, Category, Profile

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        },
        'session': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake-session',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.cache',
    SESSION_CACHE_ALIAS='session'
)
class VendorAnalyticsPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='vendor', password='password')
        # Profile created by signal, just update it
        self.profile = Profile.objects.get(user=self.user)
        self.profile.role = 'retailer'
        self.profile.save()

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', created_by=self.user)
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product', slug='test-product', price=Decimal('100.00'),
            category=self.category, vendor=self.vendor, stock_quantity=100
        )

        # Create orders
        # Order 1: 2 items, $200 total
        self.order1 = Order.objects.create(user=self.user, paid=True, first_name='A', last_name='B', email='a@b.com')
        OrderItem.objects.create(order=self.order1, product=self.product, vendor=self.vendor, price=Decimal('100.00'), quantity=2)

        # Order 2: 1 item, $100 total
        self.order2 = Order.objects.create(user=self.user, paid=True, first_name='A', last_name='B', email='a@b.com')
        OrderItem.objects.create(order=self.order2, product=self.product, vendor=self.vendor, price=Decimal('100.00'), quantity=1)

        # Total revenue should be 300

    def test_analytics_revenue(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_vendor_analytics')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check revenue
        revenue = response.data['revenue']
        self.assertEqual(float(revenue['total']), 300.00)

        # Since orders are created "now", monthly and weekly should also be 300
        self.assertEqual(float(revenue['monthly']), 300.00)
        self.assertEqual(float(revenue['weekly']), 300.00)

        # Check orders count
        self.assertEqual(response.data['orders']['total'], 2)
