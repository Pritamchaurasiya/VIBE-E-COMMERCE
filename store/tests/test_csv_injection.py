
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Order, OrderItem, Product, Vendor, Category

class CsvInjectionTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.admin_user)

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=10.00,
            vendor=self.vendor,
            category=self.category
        )

    def test_order_export_sanitization(self):
        """
        Test that CSV export sanitizes fields starting with =, +, -, @
        to prevent formula injection.
        """
        malicious_name = "=cmd|' /C calc'!A0"
        malicious_address = "+1+1"

        Order.objects.create(
            user=self.admin_user,
            first_name=malicious_name,
            last_name="Doe",
            email="test@example.com",
            address=malicious_address,
            paid=True,
            paid_amount=10.00
        )

        response = self.client.get(reverse('api_export'), {'type': 'orders'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8')

        # We expect the values to be escaped with a single quote
        # If not sanitized, these assertions will fail
        self.assertIn(f"'{malicious_name}", content)
        self.assertIn(f"'{malicious_address}", content)

    def test_user_export_sanitization(self):
        """
        Test that user export sanitizes fields.
        """
        malicious_username = "@malicious"
        User.objects.create_user(
            username=malicious_username,
            email="malicious@example.com",
            password="password123"
        )

        response = self.client.get(reverse('api_export'), {'type': 'users'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = response.content.decode('utf-8')

        # Expect sanitization
        self.assertIn(f"'{malicious_username}", content)
