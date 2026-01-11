import pytest
from django.test import TestCase
from django.db import connection, reset_queries
from store.models import Product, Category, Vendor
from store.services.recommendations import RecommendationService
from django.contrib.auth.models import User
from django.test.utils import CaptureQueriesContext

class RecommendationPerformanceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Create products
        self.products = []
        for i in range(20):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=100.00,
                category=self.category,
                vendor=self.vendor,
                is_active=True,
                stock_quantity=10
            )
            self.products.append(product)

        self.target_product = self.products[0]
        self.service = RecommendationService(user=self.user)

    def test_get_similar_products_performance(self):
        # Clear any previous queries
        reset_queries()

        with CaptureQueriesContext(connection) as ctx:
            recommendations = self.service.get_similar_products(self.target_product, limit=10)

            # Access related fields to trigger N+1 if present
            for product in recommendations:
                _ = product.category.name
                _ = product.vendor.name
                # Trigger image access if applicable
                _ = list(product.images.all())

        # With optimization: 1 main query + 1 prefetch images = 2 queries
        # Without optimization: 1 main + 10 cat + 10 vendor + 10 images = 31 queries
        # We allow a small buffer for setup/auth queries if any leak through, but < 5 is safe
        self.assertLess(len(ctx.captured_queries), 5, f"Expected < 5 queries, got {len(ctx.captured_queries)}")
