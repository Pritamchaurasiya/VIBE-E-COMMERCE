from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Vendor, Product, Category
from decimal import Decimal

class CSVInjectionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='password',
            is_staff=True
        )
        self.client.login(username='admin', password='password')

        self.vendor = Vendor.objects.create(
            name='=cmd|/C calc!A0',
            slug='malicious-vendor',
            city='Evil City'
        )
        self.category = Category.objects.create(name='Cat', slug='cat')
        self.product = Product.objects.create(
            name='=1+1',
            slug='malicious-product',
            vendor=self.vendor,
            category=self.category,
            price=Decimal('10.00'),
            is_active=True
        )

    def test_vendor_export_vulnerability(self):
        # Test Django View
        response = self.client.get(reverse('admin_export_data'), {'type': 'vendors'})
        content = response.content.decode('utf-8')
        self.assertIn("'=cmd|/C calc!A0", content)

    def test_product_export_vulnerability(self):
        # Test Django View
        response = self.client.get(reverse('admin_export_data'), {'type': 'products'})
        content = response.content.decode('utf-8')
        self.assertIn("'=1+1", content)

    def test_api_export_vulnerability(self):
        # Test DRF API View
        # Need to ensure admin permission or appropriate auth
        # ExportDataView permission_classes = [permissions.IsAdminUser]

        response = self.client.get(reverse('api_export'), {'type': 'products'})
        content = response.content.decode('utf-8')
        self.assertIn("'=1+1", content)
