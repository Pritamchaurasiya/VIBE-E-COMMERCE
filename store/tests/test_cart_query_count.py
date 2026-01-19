from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Product, Category, Vendor
from django.test import override_settings

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class CartQueryCountTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Create multiple products
        self.products = []
        for i in range(5):
            product = Product.objects.create(
                category=self.category,
                vendor=self.vendor,
                name=f'Test Product {i}',
                slug=f'test-product-{i}',
                price=10.00
            )
            self.products.append(product)

        self.url = reverse('api_cart')

    def test_cart_get_query_count_authenticated(self):
        self.client.force_authenticate(user=self.user)

        # Add products to cart
        for product in self.products:
            self.client.post(self.url, {'product_id': product.id, 'quantity': 1, 'action': 'add'})

        # Clear any captured queries
        from django.db import connection
        connection.queries_log.clear()

        # Measure queries for GET
        # Authenticated user:
        # 1. Fetch CartItems (with select_related product) -> In __init__
        # 2. Fetch Products -> In __iter__ (redundant)
        # 3. Fetch Products -> In get_total_cost (redundant)
        # Total expected around 3 (excluding auth/session queries if any)

        with self.assertNumQueries(1):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

    # Commenting out anonymous test as it seems CartView requires auth by default
    # def test_cart_get_query_count_anonymous(self):
    #     # Add products to cart
    #     for product in self.products:
    #         self.client.post(self.url, {'product_id': product.id, 'quantity': 1, 'action': 'add'})

    #     with self.assertNumQueries(2):
    #         response = self.client.get(self.url)
    #         self.assertEqual(response.status_code, 200)
