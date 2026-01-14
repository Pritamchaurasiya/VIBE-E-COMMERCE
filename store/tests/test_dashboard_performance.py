from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from store.models import Order, Product, Vendor, Category, OrderItem
from django.utils import timezone
from datetime import timedelta

class DashboardStatsPerformanceTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin_perf',
            password='password123',
            email='admin@example.com'
        )
        self.client.force_authenticate(user=self.admin_user)
        self.url = reverse('api_dashboard_stats')

        # Create some data
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=100.00,
            vendor=self.vendor,
            category=self.category
        )

        # Create orders with different statuses and dates
        now = timezone.now()

        # Today's paid order
        order1 = Order.objects.create(
            user=self.admin_user,
            first_name='Test', last_name='User',
            paid=True,
            paid_amount=100.00,
            status='processing'
        )
        OrderItem.objects.create(order=order1, product=self.product, price=100.00, quantity=1, vendor=self.vendor)

        # Yesterday's paid order (this week, this month)
        order2 = Order.objects.create(
            user=self.admin_user,
            first_name='Test', last_name='User',
            paid=True,
            paid_amount=200.00,
            status='shipped'
        )
        order2.created_at = now - timedelta(days=1)
        order2.save()
        OrderItem.objects.create(order=order2, product=self.product, price=200.00, quantity=1, vendor=self.vendor)

        # Last week's paid order (this month)
        order3 = Order.objects.create(
            user=self.admin_user,
            first_name='Test', last_name='User',
            paid=True,
            paid_amount=300.00,
            status='delivered'
        )
        order3.created_at = now - timedelta(days=8)
        order3.save()
        OrderItem.objects.create(order=order3, product=self.product, price=300.00, quantity=1, vendor=self.vendor)

        # Pending order
        order4 = Order.objects.create(
            user=self.admin_user,
            first_name='Test', last_name='User',
            paid=False,
            status='pending'
        )
        OrderItem.objects.create(order=order4, product=self.product, price=100.00, quantity=1, vendor=self.vendor)

    def test_dashboard_stats_query_count(self):
        # We optimized revenue (1 query) and order stats (1 query).
        # Other queries:
        # - Products (4)
        # - Users (4)
        # - Vendors (2)
        # - Recent orders (1)
        # - Top products (1)
        # - Tracking Config (3 queries: system_access, performance_metrics, user_actions)
        # Total confirmed: 17 queries.

        with self.assertNumQueries(17):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
