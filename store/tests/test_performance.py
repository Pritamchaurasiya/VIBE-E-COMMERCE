from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.db import connection, reset_queries
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
from rest_framework import status
from store.models import Product, Category, Vendor, Wishlist, Review
from decimal import Decimal

class ProductPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='perftest', password='password')
        self.client.force_authenticate(user=self.user)

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.category = Category.objects.create(name='Test Category', slug='test-category')

    def create_products(self, count):
        products = []
        for i in range(count):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('100.00'),
                category=self.category,
                vendor=self.vendor,
                is_active=True
            )
            products.append(product)
        return products

    def test_product_list_queries_scaling(self):
        # Create 5 products
        products = self.create_products(5)

        # Add first product to wishlist
        Wishlist.objects.create(user=self.user, product=products[0])

        # Add review to second product
        Review.objects.create(
            product=products[1],
            user=self.user,
            rating=5,
            title='Good',
            comment='Nice'
        )

        reset_queries()
        with CaptureQueriesContext(connection) as captured_5:
             response = self.client.get(reverse('api_products'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        initial_queries = len(captured_5)
        print(f"Queries for 5 products: {initial_queries}")

        # Clear products and create 10 products
        Product.objects.all().delete()
        products = self.create_products(10)

        # Add wishlist and reviews again
        Wishlist.objects.create(user=self.user, product=products[0])
        Review.objects.create(
            product=products[1],
            user=self.user,
            rating=5,
            title='Good',
            comment='Nice'
        )

        reset_queries()
        with CaptureQueriesContext(connection) as captured_10:
             response = self.client.get(reverse('api_products'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        scaled_queries = len(captured_10)
        print(f"Queries for 10 products: {scaled_queries}")

        # Performance assertion: Queries should NOT scale linearly with product count.
        # They should be constant (O(1)) relative to the number of products on the page.
        self.assertEqual(scaled_queries, initial_queries, "Query count should remain constant regardless of product count (N+1 fixed)")
        self.assertLess(scaled_queries, 10, "Query count should be low (optimized)")
