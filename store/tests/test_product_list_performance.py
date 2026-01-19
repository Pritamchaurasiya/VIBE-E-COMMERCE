
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from store.models import Vendor, Category, Product, ProductImage, Review, Wishlist
from django.db import connection
from django.test.utils import CaptureQueriesContext
import decimal

class ProductListPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')
        self.category = Category.objects.create(name='Test Category', slug='test-category')

        # Create 5 products
        self.products = []
        for i in range(5):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=decimal.Decimal('100.00'),
                category=self.category,
                vendor=self.vendor,
                is_active=True
            )
            self.products.append(product)

            # Add images
            ProductImage.objects.create(product=product, image='test.jpg')

            # Add reviews
            Review.objects.create(product=product, user=self.user, rating=5, comment='Great')

            # Add to wishlist for the user
            Wishlist.objects.create(user=self.user, product=product)

    def test_query_count(self):
        self.client.force_authenticate(user=self.user)

        # Warm up
        self.client.get(reverse('api_products'))

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(reverse('api_products'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Current expected queries:
        # 1. Count products (pagination)
        # 2. Fetch products (select_related category, vendor)
        # For each product (5 products):
        # 3. Fetch images (N+1)
        # 4. Fetch reviews (for average rating) (N+1)
        # 5. Fetch review count (N+1) - might be combined or separate depending on usage
        # 6. Check wishlist (N+1)
        # 7. Session/User related queries (maybe cached or minimal)

        print(f"\nQuery count: {len(ctx.captured_queries)}")
        for i, q in enumerate(ctx.captured_queries):
            print(f"{i+1}: {q['sql']}")
