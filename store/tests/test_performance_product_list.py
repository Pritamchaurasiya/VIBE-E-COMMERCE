
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from store.models import Product, Category, Vendor, Review
from django.db import connection
from django.test.utils import CaptureQueriesContext

class ProductListPerformanceTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        # Create categories and vendors
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Create 10 products
        self.products = []
        for i in range(10):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                category=self.category,
                vendor=self.vendor,
                price=100.00,
                stock_quantity=10,
                is_active=True
            )
            self.products.append(product)

            # Create a review for each product
            Review.objects.create(
                product=product,
                user=self.user,
                rating=5,
                comment='Great product'
            )

    def test_product_list_queries_optimized(self):
        url = reverse('api_products')

        # Warm up
        self.client.get(url)

        # Measure queries
        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        print(f"\nNumber of queries: {len(ctx.captured_queries)}")

        # We expect significantly fewer queries now.
        # 1. Count (pagination)
        # 2. Main query (annotated)
        # 3. Images (prefetched)
        # 4-13. Wishlist checks (still N+1, but review/rating/images are fixed)
        # 52 queries -> ~13 queries

        self.assertLess(len(ctx.captured_queries), 20, "Queries should be optimized (around 13)")

        # Verify data correctness
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 10)
        for product_data in data:
            self.assertEqual(product_data['review_count'], 1)
            self.assertEqual(product_data['average_rating'], 5.0)
