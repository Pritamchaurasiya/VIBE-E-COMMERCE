from decimal import Decimal
import time
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.db import connection, reset_queries
from rest_framework import status
from rest_framework.test import APIClient
from django.test.utils import CaptureQueriesContext, override_settings

from store.models import Vendor, Category, Product, Order, OrderItem

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    REST_FRAMEWORK={
        'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
        'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.SessionAuthentication'],
        'DEFAULT_THROTTLE_CLASSES': [], # Disable throttling for tests
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.gzip.GZipMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.locale.LocaleMiddleware',
    ]
)
class VendorAnalyticsPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='vendor', password='password')
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            created_by=self.user,
            city='Test City'
        )
        self.category = Category.objects.create(name='Test Category', slug='test-category')

        # Create 50 products
        products = []
        for i in range(50):
            products.append(Product(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('100.00'),
                category=self.category,
                vendor=self.vendor,
                stock_quantity=10,
                low_stock_threshold=5,
                is_active=True
            ))
        Product.objects.bulk_create(products)
        self.products = Product.objects.all()

        # Create 200 orders with 2 items each
        orders = []
        now = timezone.now()
        for i in range(200):
            orders.append(Order(
                user=self.user,
                first_name='John',
                last_name='Doe',
                email=f'john{i}@example.com',
                paid=True,
                paid_amount=Decimal('200.00'),
                created_at=now
            ))
        Order.objects.bulk_create(orders)

        all_orders = Order.objects.all()
        order_items = []
        for i, order in enumerate(all_orders):
            # Item 1
            order_items.append(OrderItem(
                order=order,
                product=self.products[i % 50],
                vendor=self.vendor,
                price=Decimal('100.00'),
                quantity=1
            ))
            # Item 2
            order_items.append(OrderItem(
                order=order,
                product=self.products[(i + 1) % 50],
                vendor=self.vendor,
                price=Decimal('100.00'),
                quantity=1
            ))
        OrderItem.objects.bulk_create(order_items)

        self.url = reverse('api_vendor_analytics')
        self.client.force_authenticate(user=self.user)

    def test_performance(self):
        # Warm up
        self.client.get(self.url)

        reset_queries()

        start_time = time.time()
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(self.url)
        end_time = time.time()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        query_count = len(context.captured_queries)
        execution_time = end_time - start_time

        print(f"\nQueries: {query_count}")
        print(f"Time: {execution_time:.4f}s")

        # Currently, it executes:
        # 1 query for products filter
        # 4 queries for overview counts (total, active, out_of_stock, low_stock)
        # 1 query for order_items filter
        # 1 query for reviews
        # 1 query for bulk orders
        # 1 query for top products
        # + Auth/Session/Vendor lookup queries

        # The main issue is fetching all order_items (400 items) into memory
        # and iterating in Python.
        # While the query count might not be huge (around 10-15), the memory usage and time
        # will grow with data.

        # If select_related was missing or loop triggered lazy loading, query count would be high.
        # But here select_related IS used, so query count is low, but processing is inefficient.

        # However, looking at 'overview' counts:
        # products.count()
        # products.filter(is_active=True).count()
        # products.filter(stock_quantity=0).count()
        # products.filter(stock_quantity__lte=...).count()
        # These are 4 separate DB hits. They can be 1.

        # And revenue calculation fetches all rows.

        # Optimized:
        # 1 query for products aggregate (replaces 4 count queries)
        # 1 query for revenue aggregate (replaces 1 filter query + in-memory processing)
        # 1 query for reviews aggregate
        # 1 query for bulk orders count
        # 1 query for top products
        # + Auth/Session/Vendor lookup queries

        # We expect significantly fewer queries now (around 6-7).
        self.assertLessEqual(query_count, 7)
