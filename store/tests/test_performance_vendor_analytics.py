from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from store.models import Vendor, Product, Category, Order, OrderItem

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'session': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
)
class VendorAnalyticsPerformanceTest(APITestCase):
    def setUp(self):
        # Create user and vendor
        self.user = User.objects.create_user(username='vendor', password='password')
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            created_by=self.user,
            email='vendor@test.com'
        )
        self.client.force_authenticate(user=self.user)

        # Create category
        self.category = Category.objects.create(name='Test Category', slug='test-category')

        # Create products
        # 1. Active, In Stock (High stock)
        self.p1 = Product.objects.create(
            name='P1', slug='p1', price=100, stock_quantity=100,
            low_stock_threshold=10, is_active=True,
            category=self.category, vendor=self.vendor
        )
        # 2. Active, Out of Stock
        self.p2 = Product.objects.create(
            name='P2', slug='p2', price=200, stock_quantity=0,
            low_stock_threshold=10, is_active=True,
            category=self.category, vendor=self.vendor
        )
        # 3. Active, Low Stock
        self.p3 = Product.objects.create(
            name='P3', slug='p3', price=300, stock_quantity=5,
            low_stock_threshold=10, is_active=True,
            category=self.category, vendor=self.vendor
        )
        # 4. Inactive
        self.p4 = Product.objects.create(
            name='P4', slug='p4', price=400, stock_quantity=100,
            low_stock_threshold=10, is_active=False,
            category=self.category, vendor=self.vendor
        )

        # Dates
        now = timezone.now()
        day_ago_2 = now - timezone.timedelta(days=2)
        day_ago_10 = now - timezone.timedelta(days=10)
        day_ago_40 = now - timezone.timedelta(days=40)

        # Create Orders
        # Order 1: Today, Paid. Item: P1 (1 qty @ 100) -> Included in Weekly, Monthly, Total
        o1 = Order.objects.create(first_name='A', email='a@a.com', paid=True)
        OrderItem.objects.create(order=o1, product=self.p1, vendor=self.vendor, price=100, quantity=1)
        # created_at is auto_now_add, so it is 'now'.

        # Order 2: 2 Days ago, Paid. Item: P1 (2 qty @ 100 = 200) -> Included in Weekly, Monthly, Total
        o2 = Order.objects.create(first_name='B', email='b@b.com', paid=True)
        o2.created_at = day_ago_2
        o2.save()
        OrderItem.objects.create(order=o2, product=self.p1, vendor=self.vendor, price=100, quantity=2)

        # Order 3: 10 Days ago, Paid. Item: P1 (1 qty @ 100) -> Included in Monthly, Total. NOT Weekly.
        o3 = Order.objects.create(first_name='C', email='c@c.com', paid=True)
        o3.created_at = day_ago_10
        o3.save()
        OrderItem.objects.create(order=o3, product=self.p1, vendor=self.vendor, price=100, quantity=1)

        # Order 4: 40 Days ago, Paid. Item: P1 (1 qty @ 100) -> Included in Total. NOT Monthly, Weekly.
        o4 = Order.objects.create(first_name='D', email='d@d.com', paid=True)
        o4.created_at = day_ago_40
        o4.save()
        OrderItem.objects.create(order=o4, product=self.p1, vendor=self.vendor, price=100, quantity=1)

        # Order 5: Today, Unpaid. Item: P1 (1 qty @ 100) -> Not counted in revenue
        o5 = Order.objects.create(first_name='E', email='e@e.com', paid=False)
        OrderItem.objects.create(order=o5, product=self.p1, vendor=self.vendor, price=100, quantity=1)

    def test_vendor_analytics_metrics(self):
        # URL for 'api_vendor_analytics'
        url = '/api/v1/vendor/analytics/'

        # Expected Values:
        # Total Revenue:
        # O1 (100) + O2 (200) + O3 (100) + O4 (100) = 500
        expected_total_revenue = 500.0

        # Monthly Revenue (Last 30 days):
        # O1 (100) + O2 (200) + O3 (100) = 400
        expected_monthly_revenue = 400.0

        # Weekly Revenue (Last 7 days):
        # O1 (100) + O2 (200) = 300
        expected_weekly_revenue = 300.0

        # Product Counts:
        # Total: 4 (P1, P2, P3, P4)
        # Active: 3 (P1, P2, P3)
        # Out of Stock: 1 (P2 - stock 0)
        # Low Stock: 1 (P3 - stock 5 <= 10) Note: P2 is also <= 10, but usually low stock implies > 0.
        # Let's check logic: products.filter(stock_quantity__lte=F('low_stock_threshold')).count()
        # P2 has 0, 0 <= 10. So P2 is counted as Low Stock in the ORIGINAL logic?
        # Original code: products.filter(stock_quantity__lte=models.F('low_stock_threshold')).count()
        # Yes, 0 is LTE threshold. So Out of Stock products are also Low Stock.
        # P2 (0 <= 10), P3 (5 <= 10). P1 (100 > 10). P4 (100 > 10).
        # So Low Stock count should be 2.

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # Verify Revenue
        self.assertEqual(float(data['revenue']['total']), expected_total_revenue)
        self.assertEqual(float(data['revenue']['monthly']), expected_monthly_revenue)
        self.assertEqual(float(data['revenue']['weekly']), expected_weekly_revenue)

        # Verify Overview
        self.assertEqual(data['overview']['total_products'], 4)
        self.assertEqual(data['overview']['active_products'], 3)
        self.assertEqual(data['overview']['out_of_stock'], 1)
        self.assertEqual(data['overview']['low_stock'], 2)
