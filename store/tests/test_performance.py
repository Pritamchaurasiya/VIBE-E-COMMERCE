from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Vendor, Category, Product, ProductImage, Review, Wishlist
from django.test.utils import CaptureQueriesContext
from django.db import connection

class ProductListPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')
        self.client.force_authenticate(user=self.user)

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='City')
        self.category = Category.objects.create(name='Category', slug='category')

        # Create 10 products with images and reviews
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
            ProductImage.objects.create(product=product, image='img.jpg', is_primary=True)
            ProductImage.objects.create(product=product, image='img2.jpg')

            # Add reviews
            Review.objects.create(product=product, user=self.user, rating=5, comment='Good')
            Review.objects.create(product=product, user=self.user2, rating=4, comment='Okay')

            # Add to wishlist for even numbered products
            if i % 2 == 0:
                Wishlist.objects.create(user=self.user, product=product)

    def test_product_list_query_count(self):
        # Warmup
        self.client.get(reverse('api_products'))

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(reverse('api_products'))

        print(f"\nQuery count: {len(ctx.captured_queries)}")
        # for q in ctx.captured_queries:
        #     print(q['sql'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if 'results' in response.data:
            results = response.data['results']
        else:
            results = response.data

        self.assertEqual(len(results), 10)

        # Expectation: Less than 10 queries.
        # Current implementation likely produces ~40 queries.
        self.assertLess(len(ctx.captured_queries), 10)
