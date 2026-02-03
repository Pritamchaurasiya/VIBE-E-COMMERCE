from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from store.models import Vendor, Category, Product, Order, OrderItem, Profile
import datetime

@override_settings(
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}},
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class VendorAnalyticsPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='vendor', password='password')
        # Profile is created by signal
        self.profile = self.user.profile
        self.profile.role = 'retailer'
        self.profile.save()

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', created_by=self.user)
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Test Cat', slug='test-cat')
        self.product = Product.objects.create(
            name='Test Product', slug='test-prod',
            category=self.category, vendor=self.vendor,
            price=100.00, stock_quantity=100
        )

        self.url = reverse('api_vendor_analytics')

    def test_revenue_calculations(self):
        # Create orders
        now = timezone.now()

        # 1. Old order (> 30 days) - 1 item, price 100
        order_old = Order.objects.create(
            first_name='Old', email='old@test.com', paid=True
        )
        Order.objects.filter(pk=order_old.pk).update(created_at=now - datetime.timedelta(days=40))
        OrderItem.objects.create(order=order_old, product=self.product, vendor=self.vendor, price=100, quantity=1)

        # 2. Monthly order (15 days ago) - 2 items, price 100
        order_month = Order.objects.create(
            first_name='Month', email='month@test.com', paid=True
        )
        Order.objects.filter(pk=order_month.pk).update(created_at=now - datetime.timedelta(days=15))
        OrderItem.objects.create(order=order_month, product=self.product, vendor=self.vendor, price=100, quantity=2)

        # 3. Weekly order (2 days ago) - 3 items, price 100
        order_week = Order.objects.create(
            first_name='Week', email='week@test.com', paid=True
        )
        Order.objects.filter(pk=order_week.pk).update(created_at=now - datetime.timedelta(days=2))
        OrderItem.objects.create(order=order_week, product=self.product, vendor=self.vendor, price=100, quantity=3)

        # 4. Unpaid order (should not count)
        order_unpaid = Order.objects.create(
            first_name='Unpaid', email='unpaid@test.com', paid=False
        )
        OrderItem.objects.create(order=order_unpaid, product=self.product, vendor=self.vendor, price=100, quantity=10)

        # Totals expected:
        # Old: 1 * 100 = 100
        # Month: 2 * 100 = 200
        # Week: 3 * 100 = 300
        # Total Revenue = 100 + 200 + 300 = 600
        # Monthly Revenue = 200 + 300 = 500 (Last 30 days includes week)
        # Weekly Revenue = 300

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data['revenue']['total'], 600.0)
        self.assertEqual(data['revenue']['monthly'], 500.0)
        self.assertEqual(data['revenue']['weekly'], 300.0)
