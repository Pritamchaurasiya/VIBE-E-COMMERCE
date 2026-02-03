
import time
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from store.models import Vendor, Product, Category, Order, OrderItem
from store.api_views import VendorAnalyticsAPIView
from rest_framework.test import APIRequestFactory, force_authenticate
from django.utils import timezone
from datetime import timedelta

@override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}, SESSION_ENGINE='django.contrib.sessions.backends.db')
class VendorAnalyticsPerformanceTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='vendor', password='password')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', created_by=self.user)
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product', slug='test-product', price=100,
            category=self.category, vendor=self.vendor
        )

        # Create 5000 orders
        print("Creating 5000 orders...")
        orders = []
        items = []
        now = timezone.now()

        # Batch create orders
        for i in range(5000):
            order = Order(
                user=self.user,
                first_name='Test',
                last_name='User',
                email='test@example.com',
                paid=True,
                created_at=now - timedelta(days=i%60) # Spread over 60 days
            )
            orders.append(order)

        Order.objects.bulk_create(orders)

        # We need to fetch back to get IDs
        created_orders = Order.objects.all()

        for order in created_orders:
            items.append(OrderItem(
                order=order,
                product=self.product,
                vendor=self.vendor,
                price=100,
                quantity=2
            ))

        OrderItem.objects.bulk_create(items)
        print("Setup complete.")

    def test_performance(self):
        view = VendorAnalyticsAPIView.as_view()
        request = self.factory.get('/api/v1/vendor/analytics/')
        force_authenticate(request, user=self.user)

        start_time = time.time()
        response = view(request)
        end_time = time.time()

        duration = end_time - start_time
        print(f"Request took {duration:.4f} seconds")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['revenue']['total'], 1000000.0) # 5000 * 2 * 100
