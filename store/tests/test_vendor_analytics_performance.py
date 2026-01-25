import time
from decimal import Decimal
from datetime import timedelta
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIClient
from store.models import Vendor, Product, Category, Order, OrderItem

class VendorAnalyticsPerformanceTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.password = 'testpass123'
        self.user = User.objects.create_user(
            username='vendor_user',
            password=self.password
        )
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            created_by=self.user,
            city='Test City'
        )
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor,
            stock_quantity=10000
        )

    def test_analytics_performance(self):
        # Create many orders
        num_orders = 1000
        orders = []

        now = timezone.now()

        for i in range(num_orders):
            orders.append(Order(
                user=self.user,
                first_name='Test',
                last_name='User',
                email=f'test{i}@example.com',
                paid=True,
                created_at=now - timedelta(days=i%40)
            ))

        Order.objects.bulk_create(orders)

        # Fetch created orders to get IDs
        saved_orders = list(Order.objects.filter(email__startswith='test'))

        order_items = []
        for order in saved_orders:
            order_items.append(OrderItem(
                order=order,
                product=self.product,
                vendor=self.vendor,
                price=self.product.price,
                quantity=2
            ))

        OrderItem.objects.bulk_create(order_items)

        url = reverse('api_vendor_analytics')

        # Measure execution time
        start_time = time.time()

        # Current implementation fetches all order items and iterates in Python.
        # It uses select_related, so query count might be low (1 for items + 1 for products + 1 for reviews + etc),
        # but the amount of data transferred and processed in Python is high.

        # Using CaptureQueriesContext to count queries if needed, or just assertNumQueries
        # We expect a certain number of queries.
        # 1. Auth check (maybe cached or not counted if force_authenticate)
        # 2. Vendor check (request.user.vendor) - Accessing related object might trigger query
        # 3. Products count
        # 4. OrderItems fetch (The BIG one)
        # 5. Reviews
        # 6. Bulk orders
        # 7. Top products

        with self.assertNumQueries(10):
             response = self.client.get(url)

        end_time = time.time()
        duration = end_time - start_time

        print(f"\nVendor Analytics Duration (1000 orders): {duration:.4f}s")

        self.assertEqual(response.status_code, 200)
        data = response.data

        # Verify correctness
        expected_revenue = num_orders * 2 * 100
        self.assertEqual(data['revenue']['total'], expected_revenue)
