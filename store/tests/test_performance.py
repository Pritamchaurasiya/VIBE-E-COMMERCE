"""
Performance tests for ProductListView.
"""
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.db import connection
from django.test.utils import CaptureQueriesContext
from store.models import Vendor, Category, Product, ProductImage, Review, Wishlist

class ProductPerformanceTest(TestCase):
    """Test cases for Product API performance."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.user = User.objects.create_user(username='perftest', password='password')
        self.client.force_authenticate(user=self.user)
        self.user2 = User.objects.create_user(username='perftest2', password='password')

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')
        self.category = Category.objects.create(name='Test Category', slug='test-category')

        # Create 10 products
        for i in range(10):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('100.00'),
                category=self.category,
                vendor=self.vendor,
                is_active=True
            )

            # Create 2 images per product
            ProductImage.objects.create(product=product, image='test.jpg')
            ProductImage.objects.create(product=product, image='test2.jpg')

            # Create 2 reviews per product
            Review.objects.create(
                product=product,
                user=self.user,
                rating=5,
                comment='Great'
            )
            Review.objects.create(
                product=product,
                user=self.user2,
                rating=4,
                comment='Good'
            )

        # Add first 5 products to wishlist
        products = Product.objects.all()[:5]
        for product in products:
            Wishlist.objects.create(user=self.user, product=product)

    def test_product_list_queries(self):
        """Test the number of queries executed by ProductListView."""
        # Warm up
        self.client.get(reverse('api_products'))

        with CaptureQueriesContext(connection) as ctx:
             response = self.client.get(reverse('api_products'))
             self.assertEqual(response.status_code, status.HTTP_200_OK)

        query_count = len(ctx)
        print(f"\nProductListView query count: {query_count}")

        # Optimized:
        # 1. Main product query (annotated)
        # 2. Images prefetch query
        # 3. Wishlist bulk fetch query
        # 4. Count query for pagination
        # Total ~ 4-5 queries.
        self.assertLess(query_count, 10, f"Expected optimized query count < 10, got {query_count}")
