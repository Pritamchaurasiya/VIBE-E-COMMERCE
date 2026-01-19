from django.test import TestCase
from store.models import Order, User
from store.api_views import ExportDataView
from store.views import _export_orders
import csv
import io

class CsvSecurityTest(TestCase):
    def test_csv_injection_api_view(self):
        user = User.objects.create_user(username='hacker', password='password')

        # Use simple payloads to avoid string escaping confusion
        order = Order.objects.create(
            user=user,
            first_name='=1+1',
            last_name='Smith',
            email='test@example.com',
            address='+1+2',
            paid_amount=100
        )

        view = ExportDataView()
        response = view._export_orders(None, None)
        content = response.content.decode('utf-8')

        # Verify the content contains sanitized payload
        # Should contain ' before the malicious characters
        self.assertIn("'=1+1", content)
        self.assertIn("'+1+2", content)

        # Verify structure
        rows = list(csv.reader(io.StringIO(content)))
        data_row = rows[1]

        # Address is column 4
        address = data_row[4]

        # In SECURE state, it matches input with prepended quote
        self.assertEqual(address, "'+1+2")
        self.assertTrue(address.startswith("'"))

    def test_csv_injection_views_helper(self):
        output = io.StringIO()
        writer = csv.writer(output)

        user = User.objects.create_user(username='hacker2', password='password')
        Order.objects.create(
            user=user,
            first_name='@SUM(1+1)',
            last_name='Jones',
            email='test2@example.com',
            address='-1+1',
            paid_amount=100
        )

        _export_orders(writer)
        content = output.getvalue()

        # Note: _export_orders concatenates first and last name
        # so output is "'@SUM(1+1) Jones"

        self.assertIn("'@SUM(1+1)", content)

        rows = list(csv.reader(io.StringIO(content)))
        data_row = rows[1]

        # Name is col 1
        name = data_row[1]
        self.assertTrue(name.startswith("'@"))
        self.assertEqual(name, "'@SUM(1+1) Jones")
