import csv
import io
from django.urls import reverse
from store.models import Order, OrderItem
from store.tests.test_utils import AdminTestCase

class CsvInjectionTest(AdminTestCase):
    def setUp(self):
        super().setUp()
        # Create an order with a malicious first name
        # We define order creation locally to avoid issues with broken test utils
        self.malicious_order = Order.objects.create(
            user=self.user,
            first_name="=1+1", # Malicious payload
            last_name="User",
            email="test@example.com",
            address="123 Test St",
            place="Test City",
            zipcode="12345",
            phone="1234567890",
            paid=True
        )

        # Create order item
        OrderItem.objects.create(
            order=self.malicious_order,
            product=self.product,
            vendor=self.vendor,
            price=self.product.price,
            quantity=1
        )

    def test_admin_export_csv_vulnerability(self):
        """Test that the CSV export IS currently vulnerable (repro) or IS sanitized (fix)."""
        url = reverse('admin_export_data') + '?type=orders'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        reader = csv.reader(io.StringIO(content))
        header = next(reader)
        # Find the row with our order
        found = False
        for row in reader:
            if str(self.malicious_order.id) == row[0]:
                found = True
                customer_name = row[1]
                # row[1] is f"{order.first_name} {order.last_name}"
                # So it should be "=1+1 User"

                # Check for sanitization
                # If it starts with '=', it's vulnerable
                if customer_name.startswith('='):
                    self.fail(f"CSV Injection vulnerability detected! Value: {customer_name}")

                # If we implemented the fix, it should start with "'"
                self.assertTrue(customer_name.startswith("'"), f"Value should be sanitized with leading quote. Got: {customer_name}")

        self.assertTrue(found, "Order not found in CSV export")

    def test_api_export_csv_vulnerability(self):
        """Test that the API CSV export IS currently vulnerable (repro) or IS sanitized (fix)."""
        url = reverse('api_export') + '?type=orders'
        # API requires admin permission which AdminTestCase provides via login_admin
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        reader = csv.reader(io.StringIO(content))
        header = next(reader)
        found = False
        for row in reader:
            if str(self.malicious_order.id) == row[0]:
                found = True
                customer_name = row[1]
                if customer_name.startswith('='):
                    self.fail(f"CSV Injection vulnerability detected in API! Value: {customer_name}")
                self.assertTrue(customer_name.startswith("'"), f"Value should be sanitized. Got: {customer_name}")

        self.assertTrue(found, "Order not found in API CSV export")
