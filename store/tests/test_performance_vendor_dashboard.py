from django.test import TestCase, Client
from django.urls import reverse
from store.models import Product, Vendor, Category, Order
from django.contrib.auth.models import User
from decimal import Decimal
from django.db import connection

class VendorDashboardPerformanceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='vendor_perf_test', password='password')
        self.vendor = Vendor.objects.create(name='Perf Vendor', created_by=self.user)
        self.category = Category.objects.create(name='Perf Cat', slug='perf-cat')

        # Create a mix of products to test different filters
        # Active, Stock > 0 (normal)
        for i in range(10):
            Product.objects.create(
                vendor=self.vendor, category=self.category,
                name=f'P1_{i}', slug=f'p1-{i}', price=Decimal('10.00'),
                is_active=True, stock_quantity=10, low_stock_threshold=5
            )

        # Active, Stock <= low_stock_threshold
        for i in range(5):
            Product.objects.create(
                vendor=self.vendor, category=self.category,
                name=f'P2_{i}', slug=f'p2-{i}', price=Decimal('10.00'),
                is_active=True, stock_quantity=2, low_stock_threshold=5
            )

        # Out of stock
        for i in range(3):
            Product.objects.create(
                vendor=self.vendor, category=self.category,
                name=f'P3_{i}', slug=f'p3-{i}', price=Decimal('10.00'),
                is_active=True, stock_quantity=0, low_stock_threshold=5
            )

        self.client.force_login(self.user)

    def test_vendor_dashboard_query_count(self):
        """
        Verify the logic of vendor dashboard stats and count queries.
        """
        # We expect:
        # 10 active normal stock
        # 5 active low stock
        # 3 out of stock
        # Total products = 18

        # Current logic in views.py (before optimization) does multiple count queries.
        # We can just verify the numbers are correct in the context for now.

        # Using CaptureQueriesContext to see how many queries are executed.
        # Originally ~37 queries (N+1 on category + multiple counts).
        # Optimized to ~17 queries.
        with self.assertNumQueries(17):
            response = self.client.get(reverse('vendor_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['products_count'], 18)
        self.assertEqual(response.context['active_products_count'], 15) # 10 + 5 (both are active and stock > 0)
        self.assertEqual(response.context['low_stock_count'], 5)
        self.assertEqual(response.context['out_of_stock_count'], 3)
