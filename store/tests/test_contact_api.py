from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Contact
import bleach

@override_settings(
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.gzip.GZipMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.locale.LocaleMiddleware',
    ],
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    SESSION_CACHE_ALIAS='default'
)
class ContactSecurityTest(TestCase):
    """Test security aspects of Contact API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_contact_form_xss_vulnerability(self):
        """
        Test that submitting XSS payload works (verifying vulnerability before fix)
        and then fails (verifying fix).
        """
        xss_payload = "<script>alert('XSS')</script>"
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': f"Hello {xss_payload}"
        }

        # Add Referer to pass SecurityTrackingMiddleware CSRF check
        # Use 127.0.0.1 as it is in ALLOWED_HOSTS
        response = self.client.post(
            reverse('api_contact'),
            data,
            HTTP_REFERER='http://127.0.0.1/'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the contact was created
        contact = Contact.objects.first()
        self.assertIsNotNone(contact)

        # After fix, the payload should be sanitized (escaped)
        # bleach.clean escapes characters like < to &lt;
        sanitized_payload = bleach.clean(xss_payload)

        self.assertNotIn(xss_payload, contact.message)
        self.assertIn(sanitized_payload, contact.message)
