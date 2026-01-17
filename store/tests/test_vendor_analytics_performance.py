from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from store.models import Vendor, Product, Category, Order, OrderItem
from rest_framework import status
from datetime import timedelta
import json
import time

class VendorAnalyticsPerformanceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='vendor', password='password')
        self.user.save()

        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            created_by=self.user,
            email='vendor@test.com'
        )

        self.category = Category.objects.create(name='Test Category', slug='test-category')

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            vendor=self.vendor,
            category=self.category,
            price=100.00,
            stock_quantity=1000
        )

        # Create a large number of orders to test performance
        self.num_orders = 1000
        self.create_orders(self.num_orders)

        # Authenticate as vendor
        self.client.force_login(self.user)

    def create_orders(self, count):
        order_items = []
        now = timezone.now()

        user = User.objects.create_user(username='customer', password='password')

        # Create orders individually to ensure created_at is set correctly
        # auto_now_add interferes with bulk_create setting the date
        for i in range(count):
            order = Order.objects.create(
                user=user,
                first_name='John',
                last_name='Doe',
                email='john@example.com',
                address='123 St',
                paid=True,
                paid_amount=100.00,
                status='confirmed'
            )
            # Manually update created_at
            order.created_at = now - timedelta(days=i % 60)
            order.save(update_fields=['created_at'])

            item = OrderItem(
                order=order,
                product=self.product,
                vendor=self.vendor,
                price=100.00,
                quantity=1
            )
            order_items.append(item)

        OrderItem.objects.bulk_create(order_items)

    def test_analytics_performance(self):
        url = reverse('api_vendor_analytics')

        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()

        duration = end_time - start_time
        print(f"\nTime taken for {self.num_orders} orders: {duration:.4f} seconds")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Verify correctness
        total_revenue = self.num_orders * 100.0
        self.assertEqual(float(data['revenue']['total']), total_revenue)

        # Roughly verifying monthly/weekly - distribution logic in setup is i % 60
        # 0-29 days ago (30 days window) -> i % 60 < 30. So roughly half.
        # But 'now' is fixed, so created_at is strictly defined.
        # i goes 0..999.
        # i=0: now
        # i=1: now - 1 day
        # ...
        # i=59: now - 59 days
        # i=60: now

        # Monthly (30 days): indices where i % 60 < 30
        expected_monthly_count = sum(1 for i in range(self.num_orders) if (i % 60) < 30)
        expected_monthly_revenue = expected_monthly_count * 100.0

        # Weekly (7 days): indices where i % 60 < 7
        expected_weekly_count = sum(1 for i in range(self.num_orders) if (i % 60) < 7)
        expected_weekly_revenue = expected_weekly_count * 100.0

        self.assertEqual(float(data['revenue']['monthly']), expected_monthly_revenue)
        self.assertEqual(float(data['revenue']['weekly']), expected_weekly_revenue)
