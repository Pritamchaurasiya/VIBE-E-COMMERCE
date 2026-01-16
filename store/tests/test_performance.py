from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Product, Category, Vendor, Review, Profile, UserCoin
from rest_framework.test import APIClient
from django.db import connection, reset_queries
from django.test.utils import CaptureQueriesContext

class PerformanceTestCase(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')

        # Create user for auth
        self.user = User.objects.create_user(username='tester', password='password')
        # Ensure profile exists if needed (signals might create it, but let's be safe)
        if not hasattr(self.user, 'profile'):
             Profile.objects.create(user=self.user)
        if not hasattr(self.user, 'coins'):
             UserCoin.objects.create(user=self.user)

        self.client.force_authenticate(user=self.user)

        # Create 10 products
        self.products = []
        for i in range(10):
            p = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                category=self.category,
                vendor=self.vendor,
                price=100.00,
                stock_quantity=10,
                is_active=True
            )
            self.products.append(p)

            # Create reviews for each product
            Review.objects.create(
                product=p,
                user=User.objects.create_user(username=f'user{i}', password='password'),
                rating=5,
                comment='Great!'
            )

    def test_product_list_queries(self):
        url = reverse('api_products')

        # Warm up
        self.client.get(url)

        reset_queries()
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)

        query_count = len(ctx.captured_queries)
        print(f"\nQueries executed: {query_count}")
        for q in ctx.captured_queries:
             print(q['sql'])

        self.assertEqual(response.status_code, 200)
        # Optimized: 1 (list) + 1 (images prefetch) + 1 (count) + N (wishlist - still N+1 but reduced).
        # Should be significantly less than 50. With 10 products, wishlist is 10 queries. Total ~13-15.
        # The previous unoptimized was > 50.
        self.assertTrue(query_count < 20, f"Expected < 20 queries (Optimized), got {query_count}")
