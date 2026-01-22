from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.db import connection, reset_queries
from django.contrib.auth.models import User
from store.models import Vendor, Category, Product

class PerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Main Product', slug='main-product', price=Decimal('100.00'),
            category=self.category, vendor=self.vendor, is_active=True
        )
        # Create 8 similar products
        for i in range(8):
            Product.objects.create(
                name=f'Product {i}', slug=f'product-{i}', price=Decimal('100.00'),
                category=self.category, vendor=self.vendor, is_active=True
            )

    def test_recommendations_query_count(self):
        url = reverse('api_recommendations', kwargs={'product_id': self.product.id})

        # Warm up
        self.client.get(url)

        reset_queries()
        # Optimized:
        # 1. Main product (with select_related)
        # 2. Category products (with select_related)
        # 3. Vendor products (with select_related)
        # 4. Price products (with select_related)
        # Total = 4

        with self.assertNumQueries(4):
             response = self.client.get(url)
             self.assertEqual(response.status_code, 200)
