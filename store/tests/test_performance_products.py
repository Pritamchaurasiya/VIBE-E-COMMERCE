from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from store.models import Product, Category, Vendor, Review, Wishlist
from django.db import connection, reset_queries
import logging

class ProductPerformanceTest(APITestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        # Create category and vendor
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Create review users
        self.reviewers = []
        for k in range(3):
            self.reviewers.append(User.objects.create_user(username=f'reviewer{k}', password='password'))

        # Create 10 products
        self.products = []
        for i in range(10):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=100.00,
                category=self.category,
                vendor=self.vendor,
                description='Test description',
                stock_quantity=10,
                is_active=True
            )
            self.products.append(product)

            # Create 3 reviews for each product
            for j in range(3):
                Review.objects.create(
                    product=product,
                    user=self.reviewers[j],
                    rating=5,
                    comment='Great product!',
                    title='Review'
                )

        # Add odd-indexed products to wishlist
        for i in range(1, 10, 2):
            Wishlist.objects.create(user=self.user, product=self.products[i])

        self.url = reverse('api_products')

    def test_product_list_query_count(self):
        reset_queries()
        # Goal is ~4 queries:
        # 1. Fetch products (with annotations and related fields)
        # 2. Count products (pagination)
        # 3. Fetch wishlist IDs (pre-fetch)
        # 4. Maybe session or user lookup

        # We allow a small margin, but definitely not 50+
        with self.assertNumQueries(4):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), 10)

            # Verify data correctness
            results = response.data['results']

            # Create map by name to check specific products
            product_map = {p['name']: p for p in results}

            # Check Product 0 (no wishlist, 3 reviews)
            p0 = product_map['Product 0']
            self.assertEqual(p0['review_count'], 3)
            self.assertEqual(p0['average_rating'], 5.0)
            self.assertFalse(p0['is_in_wishlist'])

            # Check Product 1 (in wishlist, 3 reviews)
            p1 = product_map['Product 1']
            self.assertEqual(p1['review_count'], 3)
            self.assertEqual(p1['average_rating'], 5.0)
            self.assertTrue(p1['is_in_wishlist'])
