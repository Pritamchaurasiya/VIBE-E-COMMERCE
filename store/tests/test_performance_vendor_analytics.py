
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Vendor, Category, Product, Order, OrderItem
from store.tests.test_config import TEST_USER_PASSWORD

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class VendorAnalyticsPerformanceTest(TestCase):
    """Test cases for Vendor Analytics performance optimization."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='vendor_user',
            password=TEST_USER_PASSWORD
        )
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            created_by=self.user
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )
        self.customer = User.objects.create_user(
            username='customer',
            password=TEST_USER_PASSWORD
        )

    def test_analytics_calculation(self):
        """Test that analytics calculation is correct after optimization."""
        now = timezone.now()

        # Order 1: Today (counts for daily, weekly, monthly, total)
        order1 = Order.objects.create(
            user=self.customer,
            paid=True,
            first_name='A', last_name='B', email='a@b.com'
        )
        # created_at is already now

        OrderItem.objects.create(
            order=order1,
            product=self.product,
            vendor=self.vendor,
            price=Decimal('100.00'),
            quantity=2
        ) # 200 revenue

        # Order 2: 5 days ago (counts for weekly, monthly, total)
        order2 = Order.objects.create(
            user=self.customer,
            paid=True,
            first_name='A', last_name='B', email='a@b.com'
        )
        Order.objects.filter(pk=order2.pk).update(created_at=now - timedelta(days=5))

        OrderItem.objects.create(
            order=order2,
            product=self.product,
            vendor=self.vendor,
            price=Decimal('100.00'),
            quantity=1
        ) # 100 revenue

        # Order 3: 20 days ago (counts for monthly, total)
        order3 = Order.objects.create(
            user=self.customer,
            paid=True,
            first_name='A', last_name='B', email='a@b.com'
        )
        Order.objects.filter(pk=order3.pk).update(created_at=now - timedelta(days=20))

        OrderItem.objects.create(
            order=order3,
            product=self.product,
            vendor=self.vendor,
            price=Decimal('100.00'),
            quantity=3
        ) # 300 revenue

        # Order 4: 40 days ago (counts for total only)
        order4 = Order.objects.create(
            user=self.customer,
            paid=True,
            first_name='A', last_name='B', email='a@b.com'
        )
        Order.objects.filter(pk=order4.pk).update(created_at=now - timedelta(days=40))

        OrderItem.objects.create(
            order=order4,
            product=self.product,
            vendor=self.vendor,
            price=Decimal('100.00'),
            quantity=1
        ) # 100 revenue

        # Total: 200 + 100 + 300 + 100 = 700
        # Monthly (< 30 days): 200 (0d) + 100 (5d) + 300 (20d) = 600
        # Weekly (< 7 days): 200 (0d) + 100 (5d) = 300

        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api_vendor_analytics'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(float(data['revenue']['total']), 700.0)
        self.assertEqual(float(data['revenue']['monthly']), 600.0)
        self.assertEqual(float(data['revenue']['weekly']), 300.0)
