
from decimal import Decimal
import time
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from store.models import Vendor, Category, Product, Order, OrderItem, Profile
from store.tests.test_config import TEST_USER_PASSWORD

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class VendorAnalyticsPerformanceTest(TestCase):
    """Test cases for measuring performance of Vendor Analytics API."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.password = TEST_USER_PASSWORD
        self.user = User.objects.create_user(
            username='vendor_perf',
            password=self.password
        )
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        self.profile.role = 'retailer'
        self.profile.save()

        self.vendor = Vendor.objects.create(
            name='Perf Vendor',
            slug='perf-vendor',
            created_by=self.user,
            city='Perf City'
        )

        self.category = Category.objects.create(name='Test Category', slug='test-cat')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor
        )

        # Populate with significant amount of data
        self.order_count = 1000  # Number of orders to simulate
        self.create_orders()

    def create_orders(self):
        """Create bulk orders for testing."""
        orders = []
        items = []

        now = timezone.now()

        for i in range(self.order_count):
            order = Order(
                user=self.user,
                first_name=f'Buyer {i}',
                paid=True,
                created_at=now - timezone.timedelta(days=i % 40) # Spread across last 40 days
            )
            orders.append(order)

        Order.objects.bulk_create(orders)

        # Need to fetch orders back to get IDs
        created_orders = Order.objects.all()

        for order in created_orders:
            item = OrderItem(
                order=order,
                product=self.product,
                vendor=self.vendor,
                price=self.product.price,
                quantity=1
            )
            items.append(item)

        OrderItem.objects.bulk_create(items)

    def test_analytics_performance(self):
        """Measure performance of analytics endpoint."""
        self.client.force_authenticate(user=self.user)

        start_time = time.time()
        with self.assertNumQueries(5):
            response = self.client.get(reverse('api_vendor_analytics'))
        end_time = time.time()

        duration = end_time - start_time
        print(f"\nAnalytics API Duration: {duration:.4f}s")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['revenue']['total'], self.order_count * 100.0)
