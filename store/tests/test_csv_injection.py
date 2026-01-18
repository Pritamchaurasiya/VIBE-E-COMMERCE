from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.tests.test_config import TEST_USER_PASSWORD

class CsvInjectionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password=TEST_USER_PASSWORD,
            is_staff=True
        )
        self.malicious_user = User.objects.create_user(
            username='hacker',
            password=TEST_USER_PASSWORD,
            first_name='=cmd|\' /C calc\'!A0',
            last_name='@SUM(1+1)'
        )

    def test_csv_injection_in_user_export(self):
        self.client.login(username='admin_test', password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('admin_export_data'), {'type': 'users'})

        content = response.content.decode('utf-8')

        # Check that the malicious content is present (verifying the setup)
        self.assertIn('=cmd|\' /C calc\'!A0', content)
        self.assertIn('@SUM(1+1)', content)

        # This assertion is what we expect to FAIL before the fix
        # and PASS after the fix.
        # We expect sanitization to prepend a single quote
        # So we assert that unescaped malicious strings are NOT present
        # Or specifically that escaped strings ARE present.

        # For reproduction, we'll assert that it IS safe, which will fail now.
        self.assertIn("'=cmd|' /C calc'!A0", content)
        self.assertIn("'@SUM(1+1)", content)
