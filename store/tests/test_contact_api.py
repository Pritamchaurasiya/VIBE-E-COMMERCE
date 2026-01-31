
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Contact

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
)
class ContactAPITest(TestCase):
    """Test cases for Contact API endpoints."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

    def test_contact_submission_sanitization(self):
        """Test that contact form inputs are sanitized."""
        self.client.force_authenticate(user=self.user)

        payload = {
            'name': '<script>alert("Name")</script>',
            'email': 'test@example.com',
            'message': '<script>alert("XSS")</script> This is a message.'
        }

        response = self.client.post(reverse('api_contact'), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify sanitization
        contact = Contact.objects.last()
        # bleach escapes script tags
        self.assertEqual(contact.name, '&lt;script&gt;alert("Name")&lt;/script&gt;')
        self.assertEqual(contact.message, '&lt;script&gt;alert("XSS")&lt;/script&gt; This is a message.')

    def test_contact_submission_valid(self):
        """Test valid contact submission."""
        self.client.force_authenticate(user=self.user)

        payload = {
            'name': 'Valid Name',
            'email': 'valid@example.com',
            'message': 'This is a valid message.'
        }

        response = self.client.post(reverse('api_contact'), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        contact = Contact.objects.last()
        self.assertEqual(contact.name, 'Valid Name')
        self.assertEqual(contact.message, 'This is a valid message.')

    def test_contact_submission_missing_fields(self):
        """Test submission with missing fields."""
        self.client.force_authenticate(user=self.user)

        payload = {
            'name': 'Valid Name',
            # email missing
            'message': 'Message'
        }

        response = self.client.post(reverse('api_contact'), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
