from django.test import TestCase
from django.urls import reverse
from store.utils.security import sanitize_for_csv
from store.models import Order, Product, Category, Vendor
from django.contrib.auth.models import User
from decimal import Decimal
import csv
import io

class CSVInjectionTestCase(TestCase):
    def test_sanitize_for_csv(self):
        """Test that sanitize_for_csv correctly escapes dangerous characters."""
        self.assertEqual(sanitize_for_csv("=SUM(1+1)"), "'=SUM(1+1)")
        self.assertEqual(sanitize_for_csv("+123"), "'+123")
        self.assertEqual(sanitize_for_csv("-123"), "'-123")
        self.assertEqual(sanitize_for_csv("@example.com"), "'@example.com")
        self.assertEqual(sanitize_for_csv("Safe Value"), "Safe Value")
        self.assertEqual(sanitize_for_csv(""), "")
        self.assertEqual(sanitize_for_csv(None), "")
        self.assertEqual(sanitize_for_csv(123), "123")

    def test_export_orders_sanitization(self):
        """Test that exported orders sanitize malicious fields."""
        # Create admin user for export permission
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.force_login(admin)

        # Create malicious order data
        user = User.objects.create_user('user', 'user@example.com', 'password')
        order = Order.objects.create(
            user=user,
            first_name='=cmd|',
            last_name='\' /C calc\'!A0',
            email='@malicious.com',
            address='+Dangerous Address',
            phone='-1234567890',
            paid_amount=Decimal('100.00'),
            paid=True,
            status='delivered'
        )

        # Call export API
        response = self.client.get(reverse('api_export'), {'type': 'orders'})
        self.assertEqual(response.status_code, 200)

        # Parse CSV content
        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        header = next(reader)
        row = next(reader)

        # Verify sanitization
        # Order of fields: Order ID, Customer Name, Email, Phone, Address, Total Amount, Payment Status, Order Status, Created At

        # Name check: starts with ' due to sanitize_for_csv(f"{order.first_name} {order.last_name}")
        # f"{order.first_name} {order.last_name}" is "=cmd| ' /C calc'!A0" which starts with =
        self.assertTrue(row[1].startswith("'"), f"Name not sanitized: {row[1]}")
        self.assertTrue(row[2].startswith("'"), f"Email not sanitized: {row[2]}")
        self.assertTrue(row[3].startswith("'"), f"Phone not sanitized: {row[3]}")
        self.assertTrue(row[4].startswith("'"), f"Address not sanitized: {row[4]}")

    def test_export_products_sanitization(self):
        """Test that exported products sanitize malicious fields."""
        admin = User.objects.create_superuser('admin2', 'admin2@example.com', 'password')
        self.client.force_login(admin)

        category = Category.objects.create(name='=BadCat', slug='bad-cat')
        vendor = Vendor.objects.create(name='+BadVendor', slug='bad-vendor')

        Product.objects.create(
            name='-BadProduct',
            slug='bad-product',
            category=category,
            vendor=vendor,
            price=Decimal('10.00'),
            brand='@BadBrand'
        )

        response = self.client.get(reverse('api_export'), {'type': 'products'})
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        header = next(reader)
        row = next(reader)

        # ID, Name, Category, Vendor, Price, MRP, Stock, Brand, Active, Created At
        self.assertTrue(row[1].startswith("'"), f"Product Name not sanitized: {row[1]}")
        self.assertTrue(row[2].startswith("'"), f"Category Name not sanitized: {row[2]}")
        self.assertTrue(row[3].startswith("'"), f"Vendor Name not sanitized: {row[3]}")
        self.assertTrue(row[7].startswith("'"), f"Brand not sanitized: {row[7]}")
