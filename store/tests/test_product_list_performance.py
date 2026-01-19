
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.db import connection
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from store.models import Product, Category, Vendor, ProductImage, Wishlist, Review

@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}, SESSION_ENGINE='django.contrib.sessions.backends.db')
class ProductListPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Create multiple products
        for i in range(10):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                category=self.category,
                vendor=self.vendor,
                price=100,
                is_active=True
            )
            # Add images
            ProductImage.objects.create(product=product, image='test.jpg')

            # Add reviews
            Review.objects.create(product=product, user=self.user, rating=5, comment='Nice')

        # Add some to wishlist
        Wishlist.objects.create(user=self.user, product=Product.objects.first())

    def test_product_list_query_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_products')

        # Warm up
        self.client.get(url)

        with CaptureQueriesContext(connection) as captured_queries:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

            results = response.data['results'] if 'results' in response.data else response.data
            self.assertEqual(len(results), 10)
            # Check fields to ensure serializer is working
            first_product = results[0]
            self.assertIn('images', first_product)
            self.assertIn('average_rating', first_product)
            self.assertIn('review_count', first_product)
            self.assertIn('is_in_wishlist', first_product)

        self.assertLess(len(captured_queries), 10, f"Expected < 10 queries, but got {len(captured_queries)}")
