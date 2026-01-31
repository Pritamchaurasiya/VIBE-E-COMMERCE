from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from store.models import Product, Category, Vendor, ProductImage, Review
from django.test import override_settings
from django.conf import settings

@override_settings(
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ],
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    DEBUG=True # Ensure queries are logged
)
class ProductListPerformanceTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', created_by=self.user)

        # Create 10 products with images and reviews
        for i in range(10):
            product = Product.objects.create(
                category=self.category,
                vendor=self.vendor,
                name=f'Product {i}',
                slug=f'product-{i}',
                price=100.00,
                is_active=True,
                stock_quantity=10
            )
            # Add images
            ProductImage.objects.create(product=product, image='test.jpg', is_primary=True)
            ProductImage.objects.create(product=product, image='test2.jpg', is_primary=False)

            # Add reviews
            Review.objects.create(product=product, user=self.user, rating=5, comment='Great!')
            Review.objects.create(product=product, user=self.user2, rating=4, comment='Good')

    def test_product_list_query_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_products')

        from django.db import connection, reset_queries
        reset_queries()

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if we got data
        self.assertTrue(len(response.data) > 0 or len(response.data['results']) > 0)

        query_count = len(connection.queries)
        print(f"\n\n[PERFORMANCE] Product List Query Count: {query_count}\n")

        # Fail explicitly if queries are high (unoptimized)
        if query_count > 10:
            print("[PERFORMANCE] N+1 problem detected!")
        else:
            print("[PERFORMANCE] Optimized!")
