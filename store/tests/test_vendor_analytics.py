import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from store.models import Vendor, Product, Category, Order, OrderItem
from django.utils import timezone
from datetime import timedelta
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.test import override_settings, TestCase

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    # Ensure session engine doesn't try to use redis if configured so
    SESSION_ENGINE='django.contrib.sessions.backends.db',
)
class TestVendorAnalyticsPerformance(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='vendor', password='password')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', created_by=self.user)
        self.user.vendor = self.vendor
        self.user.save()
        self.category = Category.objects.create(name='Test Category', slug='test-category')

        # Create products
        self.product1 = Product.objects.create(
            name='Product 1', slug='product-1', price=100,
            category=self.category, vendor=self.vendor, stock_quantity=10, is_active=True
        )
        self.product2 = Product.objects.create(
            name='Product 2', slug='product-2', price=200,
            category=self.category, vendor=self.vendor, stock_quantity=0, is_active=True
        )
        self.product3 = Product.objects.create(
            name='Product 3', slug='product-3', price=300,
            category=self.category, vendor=self.vendor, stock_quantity=5, is_active=True, low_stock_threshold=10
        )

        # Create orders
        self.order1 = Order.objects.create(
            user=self.user, paid=True, first_name='John', last_name='Doe', email='john@example.com'
        )
        # OrderItem created_at comes from order created_at usually?
        # OrderItem doesn't have created_at in the model def I read earlier, but Order does.
        # The view uses item.order.created_at

        OrderItem.objects.create(order=self.order1, product=self.product1, vendor=self.vendor, price=100, quantity=2) # 200 revenue

        # Order 2: 35 days ago (should not be in monthly)
        old_date = timezone.now() - timedelta(days=35)
        self.order2 = Order.objects.create(
            user=self.user, paid=True, first_name='Jane', last_name='Doe', email='jane@example.com'
        )
        self.order2.created_at = old_date
        self.order2.save()
        OrderItem.objects.create(order=self.order2, product=self.product2, vendor=self.vendor, price=200, quantity=1) # 200 revenue

        self.url = reverse('api_vendor_analytics')
        self.client.force_authenticate(user=self.user)

    def test_analytics_correctness(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        data = response.data

        # Total revenue: 200 + 200 = 400
        assert data['revenue']['total'] == 400.0

        # Monthly revenue: Only order1 (200)
        assert data['revenue']['monthly'] == 200.0

        # Overview
        assert data['overview']['total_products'] == 3
        assert data['overview']['active_products'] == 3
        assert data['overview']['out_of_stock'] == 1 # product2
        # product1: 10 - 2 = 8 (<= 10)
        # product2: 0 (<= 10)
        # product3: 5 (<= 10)
        assert data['overview']['low_stock'] == 3

    def test_query_count(self):
        # Warm up
        self.client.get(self.url)

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url)
            assert response.status_code == 200

        print(f"\nQuery count: {len(ctx.captured_queries)}")
        for i, q in enumerate(ctx.captured_queries):
            print(f"{i+1}: {q['sql']}")
