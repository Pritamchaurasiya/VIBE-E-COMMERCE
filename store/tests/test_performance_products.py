from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Vendor, Category, Product, ProductImage, Review, Wishlist

class ProductPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
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
            # Add images
            for j in range(3):
                ProductImage.objects.create(product=product, image='test.jpg', order=j)

            # Add reviews
            for j in range(3):
                user = User.objects.create_user(username=f'user{i}_{j}', password='password')
                Review.objects.create(product=product, user=user, rating=5, comment='Nice')

            # Add to wishlist (some products)
            if i % 2 == 0:
                Wishlist.objects.create(user=self.user, product=product)

    def test_product_list_queries(self):
        self.client.force_authenticate(user=self.user)

        # Warm up
        self.client.get(reverse('api_products'))

        # We expect a small number of queries if optimized.
        # Currently it should be much higher.
        # Products (1) + Count (1) + Images (10) + Wishlist (10) + AvgRating (10) + ReviewCount (10) ~ 42
        # With optimization, it should be around 4 queries:
        # 1. Count (pagination)
        # 2. Main query (annotated)
        # 3. Prefetch images
        # 4. Wishlist IDs
        with self.assertNumQueries(4):
             response = self.client.get(reverse('api_products'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
