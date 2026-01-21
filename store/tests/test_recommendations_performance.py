from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from store.models import Vendor, Category, Product

class RecommendationsPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.vendor_a = Vendor.objects.create(name='Vendor A', slug='vendor-a', city='City A')
        self.vendor_b = Vendor.objects.create(name='Vendor B', slug='vendor-b', city='City B')

        self.category_a = Category.objects.create(name='Category A', slug='category-a')
        self.category_b = Category.objects.create(name='Category B', slug='category-b')

        # Main Product: Vendor A, Category A, Price 100
        self.main_product = Product.objects.create(
            name='Main Product',
            slug='main-product',
            price=Decimal('100.00'),
            category=self.category_a,
            vendor=self.vendor_a,
            is_active=True
        )

        # 4 Products: Vendor B, Category A, Price 200 (Matches Category A)
        for i in range(4):
            Product.objects.create(
                name=f'Cat Product {i}',
                slug=f'cat-product-{i}',
                price=Decimal('200.00'),
                category=self.category_a,
                vendor=self.vendor_b,
                is_active=True
            )

        # 2 Products: Vendor A, Category B, Price 200 (Matches Vendor A)
        for i in range(2):
            Product.objects.create(
                name=f'Vendor Product {i}',
                slug=f'vendor-product-{i}',
                price=Decimal('200.00'),
                category=self.category_b,
                vendor=self.vendor_a,
                is_active=True
            )

        # 2 Products: Vendor B, Category B, Price 100 (Matches Price 100 +/- 20%)
        for i in range(2):
            Product.objects.create(
                name=f'Price Product {i}',
                slug=f'price-product-{i}',
                price=Decimal('100.00'),
                category=self.category_b,
                vendor=self.vendor_b,
                is_active=True
            )

    def test_recommendations_query_count(self):
        url = reverse('api_recommendations', kwargs={'product_id': self.main_product.id})

        # Determine expected baseline.
        # Initial query for product + 3 queries for lists = 4 queries.
        # Plus N+1 queries.
        # 8 products total.
        # For each product, we access p.category.name and p.vendor.name.
        # That's 2 extra queries per product if not fetched.
        # Total expected ~ 4 + 16 = 20 queries.
        # After optimization: 1 query for main product, 3 queries for lists (with select_related). Total 4.

        with self.assertNumQueries(4):
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['recommendations']), 8)
