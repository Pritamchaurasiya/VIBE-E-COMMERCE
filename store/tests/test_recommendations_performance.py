from rest_framework.test import APITestCase
from django.urls import reverse
from store.models import Product, Category, Vendor
from django.contrib.auth.models import User
import uuid

class RecommendationsPerformanceTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Create main product
        self.product = Product.objects.create(
            name='Main Product',
            slug='main-product',
            price=100,
            category=self.category,
            vendor=self.vendor,
            description='Main product description',
            stock_quantity=10,
            is_active=True
        )

        # Create recommendation candidates (enough to fill all criteria)
        # Category recs (need 4)
        for i in range(5):
            Product.objects.create(
                name=f'Cat Product {i}',
                slug=f'cat-product-{i}',
                price=1000, # Different price so it doesn't match price criteria
                category=self.category,
                vendor=Vendor.objects.create(name=f'Vendor {i}', slug=f'vendor-{i}'),
                description=f'Description {i}',
                stock_quantity=10,
                is_active=True
            )

        # Vendor recs (need 2)
        for i in range(3):
            Product.objects.create(
                name=f'Vendor Product {i}',
                slug=f'vendor-product-{i}',
                price=1000,
                category=Category.objects.create(name=f'Cat {i}', slug=f'cat-{i}'),
                vendor=self.vendor,
                description=f'Description {i}',
                stock_quantity=10,
                is_active=True
            )

        # Price recs (need 2)
        for i in range(3):
            Product.objects.create(
                name=f'Price Product {i}',
                slug=f'price-product-{i}',
                price=100, # Same price
                category=Category.objects.create(name=f'Price Cat {i}', slug=f'price-cat-{i}'),
                vendor=Vendor.objects.create(name=f'Price Vendor {i}', slug=f'price-vendor-{i}'),
                description=f'Description {i}',
                stock_quantity=10,
                is_active=True
            )

    def test_recommendations_query_count(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_recommendations', kwargs={'product_id': self.product.id})

        # Initial warmup
        self.client.get(url)

        # Current implementation:
        # 1. Get product
        # 2. Get category products
        # 3. Get vendor products
        # 4. Get price products
        # 5...N. Access related fields (category, vendor) for each recommendation item in the loop

        # Max recs = 8.
        # Queries without optimization: 4 + 2 * 8 = 20 queries (approx)
        # With optimization: 4 queries.

        # We expect HIGH number of queries if unoptimized.
        with self.assertNumQueries(4):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
