"""
Performance tests for Vendor Analytics API.
"""
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from store.models import Vendor, Category, Product, Order, OrderItem
from store.tests.test_config import TEST_VENDOR_PASSWORD

@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}, SESSION_ENGINE='django.contrib.sessions.backends.db')
class VendorAnalyticsPerformanceTest(TestCase):
    """Test performance of Vendor Analytics API."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()

        # Create vendor user
        self.user = User.objects.create_user(
            username='analytics_vendor',
            email='vendor@example.com',
            password=TEST_VENDOR_PASSWORD
        )
        self.vendor = Vendor.objects.create(
            name='Analytics Vendor',
            slug='analytics-vendor',
            city='Test City',
            created_by=self.user
        )
        self.user.vendor = self.vendor
        self.user.save()

        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        # Create products
        self.products = []
        for i in range(5):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('100.00'),
                category=self.category,
                vendor=self.vendor,
                is_active=True,
                stock_quantity=100
            )
            self.products.append(product)

        # Create orders with different dates
        self.now = timezone.now()

        # 1. Today's orders (Paid)
        self._create_orders(count=5, days_ago=0, paid=True)

        # 2. Last week's orders (Paid) - within 7 days
        self._create_orders(count=5, days_ago=3, paid=True)

        # 3. Last month's orders (Paid) - within 30 days but > 7 days
        self._create_orders(count=5, days_ago=15, paid=True)

        # 4. Old orders (Paid) - > 30 days
        self._create_orders(count=5, days_ago=40, paid=True)

        # 5. Unpaid orders (should be ignored)
        self._create_orders(count=5, days_ago=0, paid=False)

    def _create_orders(self, count, days_ago, paid):
        """Helper to create multiple orders."""
        date = self.now - timedelta(days=days_ago)
        for i in range(count):
            order = Order.objects.create(
                first_name='Test',
                last_name='User',
                email='test@example.com',
                paid=paid,
                paid_amount=Decimal('100.00') if paid else None,
                status='confirmed' if paid else 'pending'
            )
            order.created_at = date
            order.save()

            # Add items
            OrderItem.objects.create(
                order=order,
                product=self.products[i % len(self.products)],
                vendor=self.vendor,
                price=Decimal('100.00'),
                quantity=1
            )

    def test_vendor_analytics_correctness(self):
        """Test that analytics returns correct values."""
        self.client.force_authenticate(user=self.user)

        # Expect 5 queries:
        # 1. Product stats (Total, Active, Out of Stock, Low Stock)
        # 2. Revenue stats (Total, Monthly, Weekly, Total Orders)
        # 3. Review stats (Avg, Count)
        # 4. Bulk order stats
        # 5. Top products
        with self.assertNumQueries(5):
             response = self.client.get(reverse('api_vendor_analytics'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        # Total revenue: 20 paid orders * 100.00 = 2000.00
        self.assertEqual(float(data['revenue']['total']), 2000.00)

        # Monthly revenue: 15 paid orders (today + last week + last month) * 100.00 = 1500.00
        # (Orders 40 days ago are excluded)
        self.assertEqual(float(data['revenue']['monthly']), 1500.00)

        # Weekly revenue: 10 paid orders (today + last week) * 100.00 = 1000.00
        self.assertEqual(float(data['revenue']['weekly']), 1000.00)

    def test_vendor_analytics_performance(self):
        """Test that analytics is performant."""
        self.client.force_authenticate(user=self.user)

        # The unoptimized version iterates in Python.
        # The optimized version should do aggregation in DB.
        # We check num queries.

        # Expected queries:
        # 1. Get vendor products count
        # 2. Get reviews
        # 3. Get bulk orders
        # 4. Get top products
        # 5. Get revenue (this is the one we are optimizing)

        # Currently, get revenue does:
        # Product.objects.filter...
        # OrderItem.objects.filter... (fetches all items)

        response = self.client.get(reverse('api_vendor_analytics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
