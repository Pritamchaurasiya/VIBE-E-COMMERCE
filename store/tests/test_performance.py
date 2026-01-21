from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from store.models import Product, Category, Vendor, ProductImage, Review
from django.contrib.auth.models import User
from django.test.utils import CaptureQueriesContext
from django.db import connection

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ProductListPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')
        self.user = User.objects.create_user(username='reviewer', password='password')
        self.user2 = User.objects.create_user(username='reviewer2', password='password')

        # Create 10 products
        for i in range(10):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=100.00,
                category=self.category,
                vendor=self.vendor,
                is_active=True
            )
            # Add 2 images per product
            ProductImage.objects.create(product=product, image='test.jpg')
            ProductImage.objects.create(product=product, image='test2.jpg')

            # Add 2 reviews per product
            Review.objects.create(product=product, user=self.user, rating=5, comment='Great')
            Review.objects.create(product=product, user=self.user2, rating=4, comment='Good')

    def test_product_list_query_count(self):
        # Authenticate
        self.client.force_authenticate(user=self.user)

        # Warm up
        self.client.get(reverse('api_products'))

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(reverse('api_products'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Calculate expected queries:
        # 1 query for products (with select_related category, vendor)
        # For each of 10 products:
        #   1 query for images
        #   1 query for average rating (aggregate)
        #   1 query for review count
        # Total: 1 + 10 * 3 = 31 queries (approx)

        print(f"\nQuery count: {len(ctx.captured_queries)}")
        # We expect a low number of queries after optimization (N+1 fixed)
        self.assertLess(len(ctx.captured_queries), 10)
