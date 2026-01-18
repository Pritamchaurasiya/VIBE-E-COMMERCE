from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.urls import reverse
from store.models import Product, Vendor, Category, CartItem
from decimal import Decimal
from django.conf import settings

@override_settings(DEBUG=True)
class CartPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        self.vendor = Vendor.objects.create(name='V', slug='v')
        self.category = Category.objects.create(name='C', slug='c')

        # Create 10 products
        self.products = []
        for i in range(10):
            p = Product.objects.create(
                name=f'P{i}', slug=f'p{i}', price=Decimal('10.00'),
                vendor=self.vendor, category=self.category, is_active=True
            )
            self.products.append(p)

            CartItem.objects.create(
                cart_id=str(self.user.id),
                product=p,
                quantity=1
            )

    def test_cart_view_query_count_authenticated(self):
        url = reverse('api_cart')

        # Initial warmup
        self.client.get(url)

        # Optimized: 1 query (CartItem fetch with select_related)
        # Previous was 3.
        with self.assertNumQueries(1):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['item_count'], 10)
