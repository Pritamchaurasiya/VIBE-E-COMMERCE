from django.test import TestCase
from django.urls import reverse
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from store.models import Product, Category, Vendor

class RecommendationsPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='City')
        self.category = Category.objects.create(name='Test Category', slug='test-category')

        # Main product
        self.product = Product.objects.create(
            name='Main Product',
            slug='main-product',
            price=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )

        # 1. Same Category Products (will pick 4)
        for i in range(4):
            v = Vendor.objects.create(name=f'Vendor Cat {i}', slug=f'vendor-cat-{i}', city='City')
            Product.objects.create(
                name=f'Cat Product {i}',
                slug=f'cat-product-{i}',
                price=Decimal('500.00'),
                category=self.category,
                vendor=v,
                is_active=True
            )

        # 2. Same Vendor Products (will pick 2)
        for i in range(2):
            c = Category.objects.create(name=f'Cat Vendor {i}', slug=f'cat-vendor-{i}')
            Product.objects.create(
                name=f'Vendor Product {i}',
                slug=f'vendor-product-{i}',
                price=Decimal('500.00'),
                category=c,
                vendor=self.vendor,
                is_active=True
            )

        # 3. Similar Price Products (will pick 2)
        for i in range(2):
            c = Category.objects.create(name=f'Cat Price {i}', slug=f'cat-price-{i}')
            v = Vendor.objects.create(name=f'Vendor Price {i}', slug=f'vendor-price-{i}', city='City')
            Product.objects.create(
                name=f'Price Product {i}',
                slug=f'price-product-{i}',
                price=Decimal('100.00'),
                category=c,
                vendor=v,
                is_active=True
            )

    def test_recommendations_query_count(self):
        url = reverse('api_recommendations', kwargs={'product_id': self.product.id})

        # Warmup
        self.client.get(url)

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['recommendations']), 8)

        query_count = len(ctx.captured_queries)
        print(f"\nQuery count: {query_count}")

        # We expect significantly fewer queries now (optimized should be around 4-6)
        # Unoptimized was around 22.
        self.assertLess(query_count, 10, f"Too many queries: {query_count}. N+1 optimization might be missing.")
