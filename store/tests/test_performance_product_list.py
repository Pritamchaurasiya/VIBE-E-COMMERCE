
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.db import connection, reset_queries
from decimal import Decimal
from store.models import Vendor, Category, Product, Review, ProductImage, User

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    REST_FRAMEWORK={
        'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 20,
    }
)
class ProductListPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='City')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.user = User.objects.create_user(username='reviewer', password='password')

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

            # Add 3 reviews per product
            for j in range(3):
                user = User.objects.create_user(username=f'reviewer_{i}_{j}', password='password')
                Review.objects.create(
                    product=product,
                    user=user,
                    rating=5,
                    title=f'Review {j}',
                    comment='Great'
                )

            # Add 3 images per product
            for k in range(3):
                ProductImage.objects.create(
                    product=product,
                    image='path/to/image.jpg',
                    alt_text=f'Image {k}'
                )

    def test_product_list_queries(self):
        reset_queries()
        # Expecting drastically reduced queries (should be 3)
        with self.assertNumQueries(3):
            response = self.client.get(reverse('api_products'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Handle pagination
            if 'results' in response.data:
                self.assertEqual(len(response.data['results']), 10)
            else:
                self.assertEqual(len(response.data), 10)
