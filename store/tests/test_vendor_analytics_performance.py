
import time
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from store.models import Vendor, Product, Category, Order, OrderItem, Profile

class VendorAnalyticsPerformanceTest(APITestCase):
    def setUp(self):
        # Create user and vendor
        self.user = User.objects.create_user(username='vendor', password='password')
        # Profile is created by signal
        self.profile = Profile.objects.get(user=self.user)
        self.profile.role = 'retailer'
        self.profile.save()

        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            created_by=self.user
        )

        # Create category and product
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            vendor=self.vendor,
            price=10.00,
            stock_quantity=10000
        )

        # Authenticate
        self.client.force_authenticate(user=self.user)

        # Create orders
        self.create_orders()

    def create_orders(self):
        # Create 1000 orders
        # 100 orders > 30 days ago (should not be in monthly/weekly)
        # 100 orders between 7 and 30 days ago (should be in monthly, not weekly)
        # 800 orders < 7 days ago (should be in monthly and weekly)

        now = timezone.now()
        orders = []
        order_items = []

        # > 30 days ago
        date_old = now - timedelta(days=40)
        for i in range(100):
            order = Order(
                user=self.user,
                first_name='Test',
                last_name='User',
                email='test@example.com',
                paid=True,
                status='delivered',
                created_at=date_old
            )
            # We can't batch create easily because we need PKs for items,
            # and sqlite usually doesn't return PKs on bulk_create unless very recent django
            # So loop is fine for setup
            order.save()
            order.created_at = date_old
            order.save()

            item = OrderItem(
                order=order,
                product=self.product,
                vendor=self.vendor,
                price=10.00,
                quantity=1
            )
            order_items.append(item)

        # 7-30 days ago
        date_month = now - timedelta(days=15)
        for i in range(100):
            order = Order(
                user=self.user,
                first_name='Test',
                last_name='User',
                email='test@example.com',
                paid=True,
                status='delivered',
                created_at=date_month
            )
            order.save()
            order.created_at = date_month
            order.save()

            item = OrderItem(
                order=order,
                product=self.product,
                vendor=self.vendor,
                price=10.00,
                quantity=1
            )
            order_items.append(item)

        # < 7 days ago
        date_week = now - timedelta(days=2)
        for i in range(800):
            order = Order(
                user=self.user,
                first_name='Test',
                last_name='User',
                email='test@example.com',
                paid=True,
                status='delivered',
                created_at=date_week
            )
            order.save()
            order.created_at = date_week
            order.save()

            item = OrderItem(
                order=order,
                product=self.product,
                vendor=self.vendor,
                price=10.00,
                quantity=1
            )
            order_items.append(item)

        OrderItem.objects.bulk_create(order_items)

    def test_analytics_performance_and_correctness(self):
        url = '/api/v1/vendor/analytics/'

        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()

        duration = end_time - start_time
        print(f"\nVendor Analytics API took {duration:.4f} seconds")

        self.assertEqual(response.status_code, 200)

        # Verify correctness
        revenue_data = response.data['revenue']

        # Total: 1000 orders * 10.00 = 10000.00
        self.assertEqual(float(revenue_data['total']), 10000.00)

        # Monthly: (100 + 800) orders * 10.00 = 9000.00
        self.assertEqual(float(revenue_data['monthly']), 9000.00)

        # Weekly: 800 orders * 10.00 = 8000.00
        self.assertEqual(float(revenue_data['weekly']), 8000.00)
