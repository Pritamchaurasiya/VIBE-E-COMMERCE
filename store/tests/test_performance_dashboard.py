
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from store.models import Order, Product, Vendor, OrderItem, Category
from store.api_views import DashboardStatsView
from rest_framework.test import APIRequestFactory
from decimal import Decimal

@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}, SESSION_ENGINE='django.contrib.sessions.backends.db')
class DashboardStatsPerformanceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('admin', 'admin@example.com', 'password', is_staff=True)
        self.vendor = Vendor.objects.create(name="Test Vendor", slug="test-vendor", created_by=self.user)
        self.category = Category.objects.create(name="Test Category", slug="test-cat")

        # Create products
        self.p1 = Product.objects.create(
            name="P1", slug="p1", price=100, stock_quantity=10,
            category=self.category, vendor=self.vendor
        )
        self.p2 = Product.objects.create(
            name="P2", slug="p2", price=200, stock_quantity=0,
            category=self.category, vendor=self.vendor
        )

        # Create orders
        # Order 1: Paid, today
        o1 = Order.objects.create(
            user=self.user, paid=True, paid_amount=100, status='pending',
            first_name='A', last_name='B', email='a@b.com', address='Ad', zipcode='1', place='P', phone='1'
        )
        OrderItem.objects.create(order=o1, product=self.p1, price=100, quantity=1, vendor=self.vendor)

        # Order 2: Unpaid, today
        Order.objects.create(
            user=self.user, paid=False, paid_amount=0, status='pending',
            first_name='A', last_name='B', email='a@b.com', address='Ad', zipcode='1', place='P', phone='1'
        )

        # Order 3: Paid, 10 days ago (weekly fail, monthly pass)
        o3 = Order.objects.create(
            user=self.user, paid=True, paid_amount=200, status='delivered',
            first_name='A', last_name='B', email='a@b.com', address='Ad', zipcode='1', place='P', phone='1'
        )
        o3.created_at = timezone.now() - timezone.timedelta(days=10)
        o3.save()

    def test_dashboard_stats_values(self):
        factory = APIRequestFactory()
        view = DashboardStatsView.as_view()
        request = factory.get('/api/v1/dashboard/stats/')
        request.user = self.user

        response = view(request)
        data = response.data

        # Verify Revenue
        # Total revenue: 100 + 200 = 300
        self.assertEqual(data['revenue']['total'], 300.0)

        # Monthly revenue: 300 (both within 30 days)
        self.assertEqual(data['revenue']['monthly'], 300.0)

        # Weekly revenue: 100 (only today's order)
        self.assertEqual(data['revenue']['weekly'], 100.0)

        # Today revenue: 100
        self.assertEqual(data['revenue']['today'], 100.0)

        # Verify Orders
        self.assertEqual(data['orders']['total'], 3)
        self.assertEqual(data['orders']['paid'], 2)
        self.assertEqual(data['orders']['pending'], 2) # 1 paid, 1 unpaid
        self.assertEqual(data['orders']['delivered'], 1)

        # Verify Products
        self.assertEqual(data['products']['total'], 2)
        self.assertEqual(data['products']['active'], 2) # Default is active
        self.assertEqual(data['products']['out_of_stock'], 1) # P2

        # Verify Vendors
        self.assertEqual(data['vendors']['total'], 1)
        self.assertEqual(data['vendors']['with_products'], 1)
