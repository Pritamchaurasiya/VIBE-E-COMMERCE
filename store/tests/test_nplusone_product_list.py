from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from store.models import Product, Category, Vendor, User, Wishlist, Review
from django.db import connection
from django.test.utils import CaptureQueriesContext

class ProductListNPlusOneTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Create multiple products
        self.products = []
        for i in range(10):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                category=self.category,
                vendor=self.vendor,
                price=100.00,
                is_active=True
            )
            self.products.append(product)

            # Add some related data to trigger N+1
            Wishlist.objects.create(user=self.user, product=product)
            Review.objects.create(user=self.user, product=product, rating=5, comment="Great")

    def test_product_list_n_plus_one(self):
        url = reverse('api_products')

        # Warm up
        self.client.get(url)

        with CaptureQueriesContext(connection) as captured_queries:
            response = self.client.get(url)

        print(f"Response status: {response.status_code}")
        print(f"Query count: {len(captured_queries)}")
        # for q in captured_queries:
        #     print(q['sql'])

        self.assertTrue(len(captured_queries) < 15, f"Queries count {len(captured_queries)} is too high")
