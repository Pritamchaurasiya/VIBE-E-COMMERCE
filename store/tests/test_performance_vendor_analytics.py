import time
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework.test import APITestCase
from store.models import Vendor, Product, Order, OrderItem, Category, Profile

@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}, SESSION_ENGINE='django.contrib.sessions.backends.db')
class VendorAnalyticsPerformanceTest(APITestCase):
    def setUp(self):
        # Create User and Vendor
        self.user = User.objects.create_user(username='vendor', password='password')
        # Ensure profile exists
        if not hasattr(self.user, 'profile'):
            Profile.objects.create(user=self.user, role='retailer')

        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            created_by=self.user
        )

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=10.00,
            category=self.category,
            vendor=self.vendor,
            stock_quantity=10000
        )

        self.client.force_authenticate(user=self.user)
        self.url = '/api/v1/vendor/analytics/'

    def test_analytics_performance(self):
        count = 3000
        now = timezone.now()

        buyer = User.objects.create_user(username='buyer', password='password')

        # Create Orders with specific dates
        old_date = now - timedelta(days=40)
        month_date = now - timedelta(days=15)
        week_date = now - timedelta(days=2)

        order_old = Order.objects.create(
            user=buyer, paid=True, status='confirmed',
            first_name='Buyer', email='buyer@example.com',
            created_at=old_date
        )
        # Hack to set created_at because auto_now_add overrides it on creation
        Order.objects.filter(id=order_old.id).update(created_at=old_date)

        order_month = Order.objects.create(
            user=buyer, paid=True, status='confirmed',
            first_name='Buyer', email='buyer@example.com'
        )
        Order.objects.filter(id=order_month.id).update(created_at=month_date)

        order_week = Order.objects.create(
            user=buyer, paid=True, status='confirmed',
            first_name='Buyer', email='buyer@example.com'
        )
        Order.objects.filter(id=order_week.id).update(created_at=week_date)

        items = []
        # 1000 items for old order (should be in total, but not monthly/weekly)
        for _ in range(1000):
            items.append(OrderItem(order=order_old, product=self.product, vendor=self.vendor, price=10.00, quantity=1))

        # 1000 items for month order (should be in total and monthly, but not weekly)
        for _ in range(1000):
            items.append(OrderItem(order=order_month, product=self.product, vendor=self.vendor, price=10.00, quantity=1))

        # 1000 items for week order (should be in total, monthly, and weekly)
        for _ in range(1000):
            items.append(OrderItem(order=order_week, product=self.product, vendor=self.vendor, price=10.00, quantity=1))

        OrderItem.objects.bulk_create(items)

        # Warmup (optional, but good for stability)
        # self.client.get(self.url)

        # Measurement
        start_time = time.time()
        response = self.client.get(self.url)
        end_time = time.time()

        duration = end_time - start_time
        print(f"\nPerformance Test - Duration: {duration:.4f} seconds for {count} items")

        self.assertEqual(response.status_code, 200)
        data = response.data

        # Verify calculations
        # Total revenue = 3000 * 10 * 1 = 30000
        # Monthly revenue (>= 30 days ago) = Month (1000) + Week (1000) = 2000 * 10 = 20000
        # Weekly revenue (>= 7 days ago) = Week (1000) = 1000 * 10 = 10000

        self.assertEqual(data['revenue']['total'], 30000.0)
        self.assertEqual(data['revenue']['monthly'], 20000.0)
        self.assertEqual(data['revenue']['weekly'], 10000.0)
