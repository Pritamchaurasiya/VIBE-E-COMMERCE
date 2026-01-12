from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from store.models import Order, Product, Vendor, Category
from django.utils import timezone
import datetime

class DashboardStatsPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.force_authenticate(user=self.admin)

        # Create some data
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product', slug='test-product',
            category=self.category, vendor=self.vendor, price=100
        )

        # Create orders in different states
        for i in range(5):
            Order.objects.create(
                user=self.admin, first_name=f'User{i}', last_name='Test',
                email=f'user{i}@example.com', paid=True, paid_amount=100,
                status='delivered'
            )

        for i in range(3):
            Order.objects.create(
                user=self.admin, first_name=f'User{i}', last_name='Test',
                email=f'user{i}@example.com', paid=False,
                status='pending'
            )

        self.url = reverse('api_dashboard_stats')

    def test_query_count(self):
        # Warm up
        self.client.get(self.url)

        # Measure
        # We expect around 7-8 queries now:
        # 1. User
        # 2. Session/Auth
        # 3. Revenue stats
        # 4. Order stats
        # 5. Product stats
        # 6. User stats
        # 7. Vendor stats
        # 8. Recent orders
        # 9. Top products

        # Previously it was 20+
        # Now we optimized it to 8 queries!

        with self.assertNumQueries(8):
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
