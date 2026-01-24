from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.test import override_settings
from store.models import Vendor, Category, Product, Review, ProductImage

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ProductListPerformanceTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('reviewer', 'reviewer@example.com', 'password')
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
            # Create reviews
            Review.objects.create(
                product=product,
                user=self.user,
                rating=5,
                comment='Great'
            )
            # Create images
            ProductImage.objects.create(
                product=product,
                image='products/test.jpg'
            )

    def test_product_list_performance(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_products')

        # Capture queries
        # Expected queries:
        # 1. Count (pagination)
        # 2. Main product query (annotated)
        # 3. Prefetch images
        # 4. Wishlist lookup (batch)

        with self.assertNumQueries(4):
             response = self.client.get(url)
             self.assertEqual(response.status_code, status.HTTP_200_OK)
