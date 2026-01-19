from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from store.models import Order, Product, Vendor, Category, OrderItem

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class DashboardStatsPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin', password='password', is_staff=True, is_superuser=True
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create some test data
        vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        category = Category.objects.create(name='Test Category', slug='test-category')

        # Products
        # Set low_stock_threshold to 1 to avoid them being counted as low stock (since stock is 10)
        p1 = Product.objects.create(name='Active', price=10, vendor=vendor, category=category, is_active=True, stock_quantity=10, low_stock_threshold=1, slug='active')
        Product.objects.create(name='Inactive', price=10, vendor=vendor, category=category, is_active=False, stock_quantity=10, low_stock_threshold=1, slug='inactive')
        Product.objects.create(name='OOS', price=10, vendor=vendor, category=category, is_active=True, stock_quantity=0, slug='oos')
        Product.objects.create(name='Low Stock', price=10, vendor=vendor, category=category, is_active=True, stock_quantity=2, low_stock_threshold=5, slug='low-stock')

        # Orders
        o1 = Order.objects.create(paid=True, paid_amount=100, status='delivered')
        OrderItem.objects.create(order=o1, product=p1, price=100, quantity=1, vendor=vendor)

        o2 = Order.objects.create(paid=True, paid_amount=50, status='shipped')
        OrderItem.objects.create(order=o2, product=p1, price=50, quantity=1, vendor=vendor)

        Order.objects.create(paid=False, paid_amount=0, status='pending')
        Order.objects.create(paid=False, paid_amount=0, status='cancelled')

        # Create an order for today (auto_now_add makes it today)
        o3 = Order.objects.create(paid=True, paid_amount=20, status='processing')
        OrderItem.objects.create(order=o3, product=p1, price=20, quantity=1, vendor=vendor)


    def test_dashboard_stats_queries(self):
        url = reverse('api_dashboard_stats')

        # Optimized to ~6 queries.
        with self.assertNumQueries(6):
             response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.data

        # Verify correctness
        self.assertEqual(data['products']['total'], 4)
        self.assertEqual(data['products']['active'], 3)
        self.assertEqual(data['products']['out_of_stock'], 1)
        self.assertEqual(data['products']['low_stock'], 1)

        self.assertEqual(data['orders']['total'], 5)
        self.assertEqual(data['orders']['paid'], 3)
        self.assertEqual(data['orders']['pending'], 1)
        self.assertEqual(data['orders']['processing'], 1)
        self.assertEqual(data['orders']['shipped'], 1)
        self.assertEqual(data['orders']['delivered'], 1)
        self.assertEqual(data['orders']['cancelled'], 1)

        # Revenue verification (100 + 50 + 20 = 170)
        self.assertEqual(data['revenue']['total'], 170.0)
