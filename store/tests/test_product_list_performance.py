from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Category, Product, Vendor, ProductImage, Wishlist, Review

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ProductListPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.category = Category.objects.create(name='Test Category', slug='test-category')

        # Create 10 products with related data to trigger N+1
        for i in range(10):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('100.00'),
                category=self.category,
                vendor=self.vendor,
                is_active=True
            )
            # Add image
            ProductImage.objects.create(product=product, image='test.jpg')
            # Add wishlist item (for even products)
            if i % 2 == 0:
                Wishlist.objects.create(user=self.user, product=product)
            # Add review
            Review.objects.create(
                product=product,
                user=self.user,
                rating=5,
                comment='Great'
            )

    def test_product_list_queries(self):
        # Warm up
        self.client.get(reverse('api_products'))

        # Measure
        # Expected queries:
        # 1. Pagination count
        # 2. Main product query (with annotations)
        # 3. Images prefetch
        # 4. Wishlist IDs fetch
        with self.assertNumQueries(4):
            self.client.get(reverse('api_products'))
