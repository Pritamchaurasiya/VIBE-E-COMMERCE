from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from store.api_views import ExportDataView
import csv
import io

class TestCSVInjection(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ExportDataView.as_view()
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'password')

    def test_csv_injection_user_export(self):
        # Create a user with a malicious formula as first name
        malicious_name = "=1+1"
        User.objects.create_user(
            username='malicious',
            email='bad@example.com',
            password='password',
            first_name=malicious_name,
            last_name='User'
        )

        request = self.factory.get('/api/export/?type=users')
        request.user = self.user
        response = self.view(request)

        content = response.content.decode('utf-8')

        # We parse the CSV to check the exact value
        f = io.StringIO(content)
        reader = csv.reader(f)
        header = next(reader)

        found_sanitized = False
        found_unsanitized = False

        for row in reader:
            if row[1] == 'malicious': # username is 2nd column
                # first name is 3rd column?
                # Header: 'ID', 'Username', 'Email', 'First Name', 'Last Name', ...
                first_name_idx = 3
                first_name = row[first_name_idx]

                if first_name == malicious_name:
                    found_unsanitized = True
                elif first_name == "'" + malicious_name:
                    found_sanitized = True

        self.assertTrue(found_sanitized, "The malicious input should be escaped in the CSV export")
