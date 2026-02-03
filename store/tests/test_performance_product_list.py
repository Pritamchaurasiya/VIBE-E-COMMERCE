from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.db import connection, reset_queries
from store.models import Product, Category, Vendor, ProductImage, Review
from django.contrib.auth.models import User
from django.test import override_settings

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ProductListPerformanceTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')
        self.user = User.objects.create_user(username='testuser', password='password')

        # Create extra users for reviews
        self.reviewers = []
        for i in range(5):
            self.reviewers.append(User.objects.create_user(username=f'reviewer{i}', password='password'))

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
            # Create 5 images per product
            for j in range(5):
                ProductImage.objects.create(
                    product=product,
                    image=f'products/image_{i}_{j}.jpg',
                    alt_text=f'Image {j}'
                )
            # Create 5 reviews per product
            for k in range(5):
                Review.objects.create(
                    product=product,
                    user=self.reviewers[k],
                    rating=5,
                    title=f'Review {k}',
                    comment='Great!'
                )

        # Authenticate
        self.client.force_authenticate(user=self.user)

    def test_product_list_queries(self):
        url = reverse('api_products')

        # Clear any startup queries
        reset_queries()

        # Current unoptimized behavior triggers ~32 queries.
        # We assert a lower number to fail the test and confirm the issue.
        # Optimized behavior should be 3 queries:
        # 1. Count query (pagination)
        # 2. Main product query (with annotations for ratings/wishlist)
        # 3. Prefetch images (batch fetch)
        with self.assertNumQueries(3):
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        # Verify fields are present
        first_product = response.data['results'][0]
        self.assertEqual(len(first_product['images']), 5)
        self.assertEqual(first_product['review_count'], 5)
        self.assertEqual(float(first_product['average_rating']), 5.0)
