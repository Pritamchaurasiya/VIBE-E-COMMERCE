
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Order, Product, Vendor, Category, OrderItem

class DashboardStatsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        self.user = User.objects.create_user(
            username='user',
            password='password'
        )

        self.vendor = Vendor.objects.create(name="Test Vendor", slug="test-vendor", city="Test City")
        self.category = Category.objects.create(name="Test Category", slug="test-category")

        # Create products
        self.p1 = Product.objects.create(
            name="P1", slug="p1", price=Decimal('100.00'), stock_quantity=10,
            vendor=self.vendor, category=self.category, is_active=True
        )
        self.p2 = Product.objects.create(
            name="P2", slug="p2", price=Decimal('200.00'), stock_quantity=0,
            vendor=self.vendor, category=self.category, is_active=True
        )

        # Create orders
        self.order1 = Order.objects.create(
            user=self.user, first_name="John", last_name="Doe", email="j@d.com",
            address="Addr", zipcode="123", place="Place", phone="123",
            paid_amount=Decimal('100.00'), paid=True, status='delivered'
        )
        OrderItem.objects.create(order=self.order1, product=self.p1, vendor=self.vendor, price=Decimal('100.00'), quantity=1)

        self.order2 = Order.objects.create(
            user=self.user, first_name="John", last_name="Doe", email="j@d.com",
            address="Addr", zipcode="123", place="Place", phone="123",
            paid_amount=Decimal('200.00'), paid=False, status='pending'
        )

    def test_dashboard_stats_permission(self):
        # Unauthenticated
        url = reverse('api_dashboard_stats')
        response = self.client.get(url)
        self.assertIn(response.status_code, [401, 403])

        # Normal user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_dashboard_stats_data(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('api_dashboard_stats')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.data

        # Check structure
        self.assertIn('revenue', data)
        self.assertIn('orders', data)
        self.assertIn('products', data)
        self.assertIn('users', data)
        self.assertIn('vendors', data)

        # Check values
        self.assertEqual(data['revenue']['total'], 100.0) # Only paid orders
        self.assertEqual(data['orders']['total'], 2)
        self.assertEqual(data['orders']['paid'], 1)
        self.assertEqual(data['orders']['pending'], 1)
        self.assertEqual(data['orders']['delivered'], 1)

        self.assertEqual(data['products']['total'], 2)
        self.assertEqual(data['products']['active'], 2)
        self.assertEqual(data['products']['out_of_stock'], 1)

        # Vendor count. 1 vendor.
        self.assertEqual(data['vendors']['total'], 1)
        # Vendor with products: this vendor has products.
        self.assertEqual(data['vendors']['with_products'], 1)
