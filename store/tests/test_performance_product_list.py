
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from store.models import Product, Category, Vendor, Review, ProductImage, Wishlist, Profile, UserCoin
from django.test import override_settings

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        'session': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ProductListPerformanceTest(APITestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username='testuser', password='password')
        # Profile is created by signal, so we get it instead of creating it
        self.profile = Profile.objects.get(user=self.user)
        self.coins = UserCoin.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

        # Create another user for second review
        self.user2 = User.objects.create_user(username='testuser2', password='password')

        # Create category and vendor
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Create products
        self.num_products = 10
        self.products = []
        for i in range(self.num_products):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=100.00,
                stock_quantity=10,
                category=self.category,
                vendor=self.vendor,
                is_active=True
            )
            self.products.append(product)

            # Add images
            ProductImage.objects.create(product=product, image='test.jpg', alt_text='Test Image')
            ProductImage.objects.create(product=product, image='test2.jpg', alt_text='Test Image 2')

            # Add reviews (unique user per product)
            Review.objects.create(product=product, user=self.user, rating=5, title='Good', comment='Nice')
            Review.objects.create(product=product, user=self.user2, rating=4, title='Okay', comment='Fine')

            # Add to wishlist for some products
            if i % 2 == 0:
                Wishlist.objects.create(user=self.user, product=product)

    def test_product_list_queries(self):
        url = reverse('api_products')

        # Warmup query (to load content types, etc.)
        self.client.get(url)

        # Capture queries
        # Optimized:
        # 1 (Product count)
        # 1 (Product list with annotations for reviews/ratings/wishlist)
        # 1 (Product Images prefetch)
        # Total 3 queries.
        with self.assertNumQueries(3):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), self.num_products)
