from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from store.models import Product, Order, Vendor, Category, OrderItem
from store.tests.test_config import TEST_ADMIN_PASSWORD

class DashboardPerformanceTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        self.client.force_authenticate(user=self.admin)

        # Create some data
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')
        self.category = Category.objects.create(name='Test Category', slug='test-category')

        for i in range(5):
            p = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=100.00,
                category=self.category,
                vendor=self.vendor,
                stock_quantity=10,
                low_stock_threshold=5
            )
            # Create orders
            o = Order.objects.create(
                user=self.admin,
                first_name='Admin',
                last_name='User',
                email='admin@example.com',
                address='123 Test St',
                zipcode='12345',
                place='Test City',
                phone='1234567890',
                paid=True,
                paid_amount=100.00,
                status='delivered'
            )
            OrderItem.objects.create(
                order=o,
                product=p,
                vendor=self.vendor,
                price=100.00,
                quantity=1
            )

    def test_dashboard_stats_query_count(self):
        url = reverse('api_dashboard_stats')

        # Initial warmup
        self.client.get(url)

        # Count queries
        # Optimized from ~20 to 7 queries
        with self.assertNumQueries(7):
            response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
