from django.test import TestCase, override_settings
from django.urls import reverse
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from store.models import Vendor, Category, Product, Review, ProductImage
from django.contrib.auth.models import User

@override_settings(
    DEBUG=True,
    CACHES={
        'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
        'session': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ProductPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
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
            for j in range(2):
                ProductImage.objects.create(product=product, order=j, image=f'products/img_{i}_{j}.jpg')

            # Create 2 reviews per product
            for k in range(2):
                user = User.objects.create_user(username=f'user{i}_{k}', password='password')
                Review.objects.create(
                    product=product,
                    user=user,
                    rating=5,
                    title='Great',
                    comment='Awesome product'
                )

    def test_product_list_queries(self):
        url = reverse('api_products')
        user = User.objects.create_user(username='tester', password='password')
        self.client.force_authenticate(user=user)

        # Warmup (optional, but good practice)
        self.client.get(url)

        # Capture queries
        with CaptureQueriesContext(connection) as captured_queries:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), 10)

        print(f"Queries executed: {len(captured_queries)}")
        # If unoptimized, it should be > 30 (1 main + 10 images + 10 ratings + 10 reviews count + 10 wishlist)
        # 10 products.
        self.assertLess(len(captured_queries), 10, f"Too many queries: {len(captured_queries)}")
