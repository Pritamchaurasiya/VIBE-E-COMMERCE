from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from store.models import Product, Category, Vendor
from decimal import Decimal
from django.test.utils import CaptureQueriesContext
from django.db import connection

class RecommendationsPerfRegressionTest(TestCase):
    """Regression test for RecommendationsView performance."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Main product
        self.product = Product.objects.create(
            name='Main Product',
            slug='main-product',
            price=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor,
            description='Test',
            stock_quantity=10,
            is_active=True
        )

        # Create products to populate recommendations
        # 4 same category
        self.other_vendor = Vendor.objects.create(name='Other Vendor', slug='other-vendor')
        for i in range(4):
            Product.objects.create(
                name=f'Cat Product {i}',
                slug=f'cat-product-{i}',
                price=Decimal('500.00'),
                category=self.category,
                vendor=self.other_vendor,
                is_active=True
            )

        # 2 same vendor
        self.other_category = Category.objects.create(name='Other Category', slug='other-category')
        for i in range(2):
            Product.objects.create(
                name=f'Vendor Product {i}',
                slug=f'vendor-product-{i}',
                price=Decimal('500.00'),
                category=self.other_category,
                vendor=self.vendor,
                is_active=True
            )

        # 2 similar price
        for i in range(2):
            Product.objects.create(
                name=f'Price Product {i}',
                slug=f'price-product-{i}',
                price=Decimal('100.00'),
                category=self.other_category,
                vendor=self.other_vendor,
                is_active=True
            )

        self.url = reverse('api_recommendations', kwargs={'product_id': self.product.id})

    def test_recommendations_query_count_optimized(self):
        """
        Verify that RecommendationsView uses minimal queries.
        Expected:
        1. Get main product (select_related)
        2. Get category products (select_related)
        3. Get vendor products (select_related)
        4. Get price products (select_related)
        Total should be around 4 queries.
        """
        # Warm up
        self.client.get(self.url)

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        # We allow a small buffer for potential middleware queries, but it should be well below the unoptimized count (~20)
        # Ideally 4, maybe +1-2 for auth/session if applicable (though we are anonymous here)
        # In my manual test it was exactly 4.
        self.assertLessEqual(len(ctx.captured_queries), 6, f"Expected <= 6 queries, got {len(ctx.captured_queries)}")
