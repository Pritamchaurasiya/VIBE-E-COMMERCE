
import time
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase, override_settings, modify_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from store.models import Vendor, Category, Product, Order, OrderItem

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    REST_FRAMEWORK={
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.SessionAuthentication',
        ],
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
        'DEFAULT_THROTTLE_CLASSES': [],
    }
)
@modify_settings(MIDDLEWARE={'remove': 'store.tracking_middleware.SecurityTrackingMiddleware'})
class VendorAnalyticsPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = 'testpass123'
        self.user = User.objects.create_user(username='vendor_user', password=self.password)
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            city='Test City',
            created_by=self.user
        )
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('10.00'),
            category=self.category,
            vendor=self.vendor
        )

        # Create a large number of orders/items to simulate load
        self.order_count = 500
        orders = []
        items = []
        now = timezone.now()

        # Bulk create orders
        for i in range(self.order_count):
            order = Order(
                user=self.user,
                first_name=f'Buyer {i}',
                last_name='Doe',
                email=f'buyer{i}@example.com',
                paid=True,
                paid_amount=Decimal('10.00'),
                created_at=now
            )
            orders.append(order)

        Order.objects.bulk_create(orders)

        # Retrieve created orders to get IDs
        created_orders = Order.objects.all()

        for order in created_orders:
            item = OrderItem(
                order=order,
                product=self.product,
                vendor=self.vendor,
                price=Decimal('10.00'),
                quantity=1
            )
            items.append(item)

        OrderItem.objects.bulk_create(items)

    def test_vendor_analytics_performance(self):
        self.client.force_authenticate(user=self.user)

        start_time = time.time()
        response = self.client.get(reverse('api_vendor_analytics'))
        end_time = time.time()

        duration = end_time - start_time
        print(f"\nVendor Analytics Request took: {duration:.4f} seconds for {self.order_count} orders")

        self.assertEqual(response.status_code, 200)
        data = response.data

        # Verify correctness
        expected_revenue = self.order_count * 10.00
        self.assertEqual(float(data['revenue']['total']), expected_revenue)
        self.assertEqual(float(data['revenue']['monthly']), expected_revenue)
        self.assertEqual(float(data['revenue']['weekly']), expected_revenue)
