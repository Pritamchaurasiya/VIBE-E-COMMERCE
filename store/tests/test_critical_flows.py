from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from store.models import Product, Category, Vendor, Order, Profile, UserCoin

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class CriticalFlowsTest(APITestCase):
    def setUp(self):
        # Create test data
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@example.com')
        # Ensure profile and coin exist (signals might handle this but explicit creation is safe for tests)
        Profile.objects.get_or_create(user=self.user)
        UserCoin.objects.get_or_create(user=self.user)

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=100.00,
            stock_quantity=10,
            category=self.category,
            vendor=self.vendor,
            is_active=True
        )
        self.login_url = reverse('login') # Assuming URL name is 'login' based on api_views or urls
        # Actually in DRF it might be under /api/v1/auth/login/
        # I'll use the hardcoded path if reverse fails or just guess standard DRF
        self.login_url = '/api/v1/auth/login/'
        self.cart_url = '/api/v1/cart/'
        self.order_url = '/api/start_order/'

    def test_full_order_flow(self):
        # 1. Login
        login_response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        token = login_response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)

        # 2. View Product
        product_url = f'/api/v1/products/{self.product.slug}/'
        response = self.client.get(product_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

        # 3. Add to Cart
        cart_data = {
            'product_id': self.product.id,
            'quantity': 2,
            'action': 'add'
        }
        response = self.client.post(self.cart_url, cart_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify cart
        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['quantity'], 2)

        # 4. Checkout (Start Order)
        order_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'address': '123 Test St',
            'zipcode': '12345',
            'place': 'Test City',
            'phone': '1234567890',
            'payment_method': 'cod'
        }
        response = self.client.post(self.order_url, order_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        order_id = response.data['order_id']

        # Verify Order Created
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product, self.product)
