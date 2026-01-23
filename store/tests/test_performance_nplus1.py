
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from store.models import Vendor, Category, Product, ProductImage, Review, Wishlist
from decimal import Decimal
from django.test.utils import CaptureQueriesContext
from django.db import connection

class ProductListPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
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
            # Create related objects to trigger N+1
            ProductImage.objects.create(product=product, image='test.jpg')
            Review.objects.create(
                product=product,
                user=self.user,
                rating=5,
                comment='Great!'
            )
            # Add some to wishlist to trigger that check
            if i % 2 == 0:
                Wishlist.objects.create(user=self.user, product=product)
            products.append(product)
        return products

    def test_n_plus_one_problem(self):
        # Create 5 products
        self.create_products(5)

        # Measure queries for 5 products
        with CaptureQueriesContext(connection) as capture5:
            response = self.client.get(reverse('api_products'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        queries_5 = len(capture5)

        # Clear existing data to strictly control count
        Product.objects.all().delete()
        Vendor.objects.all().delete()
        self.vendor = Vendor.objects.create(name='Test Vendor 2', slug='test-vendor-2')

        # Create 10 products
        self.create_products(10)

        # Measure queries for 10 products
        with CaptureQueriesContext(connection) as capture10:
            response = self.client.get(reverse('api_products'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        queries_10 = len(capture10)

        print(f"Queries for 5 products: {queries_5}")
        print(f"Queries for 10 products: {queries_10}")

        self.assertLess(queries_10 - queries_5, 5,
                        f"N+1 detected! 5 products: {queries_5} queries, 10 products: {queries_10} queries. "
                        f"Difference is {queries_10 - queries_5}, expected near 0.")
