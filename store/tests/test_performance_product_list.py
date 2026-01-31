
import time
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.conf import settings
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from store.models import Product, Category, Vendor, ProductImage, Review, Wishlist
from django.db import connection, reset_queries

# Filter out middlewares that might cause issues in tests (like those requiring Redis)
TEST_MIDDLEWARE = [m for m in settings.MIDDLEWARE if 'tracking_middleware' not in m]

@override_settings(
    MIDDLEWARE=TEST_MIDDLEWARE,
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ProductListPerformanceTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Create 20 products
        for i in range(20):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                category=self.category,
                vendor=self.vendor,
                price=100.00,
                is_active=True
            )
            # Add images
            ProductImage.objects.create(product=product, image='test.jpg')
            # Add reviews
            Review.objects.create(product=product, user=self.user, rating=5, comment='Great')
            # Add to wishlist (for half of them)
            if i % 2 == 0:
                Wishlist.objects.create(user=self.user, product=product)

    def test_product_list_query_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_products')

        reset_queries()
        with CaptureQueriesContext(connection) as ctx:
             response = self.client.get(url)

        print(f"\nNumber of queries: {len(ctx.captured_queries)}")
        # Verify it is efficient now
        self.assertLess(len(ctx.captured_queries), 15)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify correctness
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 20)

        # Product 0: In wishlist, has rating 5
        p0 = next(p for p in results if p['slug'] == 'product-0')
        self.assertTrue(p0['is_in_wishlist'], "Product 0 should be in wishlist")
        self.assertEqual(len(p0['images']), 1)
        self.assertEqual(p0['average_rating'], 5.0)
        self.assertEqual(p0['review_count'], 1)

        # Product 1: Not in wishlist, has rating 5
        p1 = next(p for p in results if p['slug'] == 'product-1')
        self.assertFalse(p1['is_in_wishlist'], "Product 1 should NOT be in wishlist")
        self.assertEqual(len(p1['images']), 1)
        self.assertEqual(p1['average_rating'], 5.0)
