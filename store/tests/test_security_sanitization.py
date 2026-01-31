from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Contact, BulkOrder, Product, Vendor, Category
import bleach

# Exclude SecurityTrackingMiddleware to test bleach sanitization without WAF blocking
TEST_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    # 'store.tracking_middleware.SecurityTrackingMiddleware',  <-- Excluded
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'store.tracking_middleware.SilentTrackingMiddleware',
]

# Override caches to use LocMemCache instead of Redis to avoid connection errors during tests
TEST_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Override throttling to avoid Redis usage
TEST_REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [], # Disable throttling for tests
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

@override_settings(
    MIDDLEWARE=TEST_MIDDLEWARE,
    CACHES=TEST_CACHES,
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    REST_FRAMEWORK=TEST_REST_FRAMEWORK
)
class SecuritySanitizationTest(TestCase):
    """Test security sanitization in API views."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_contact_form_sanitization(self):
        """Test that contact form inputs are sanitized."""
        # Authenticate to bypass permission checks if any
        self.client.force_authenticate(user=self.user)

        malicious_input = "<script>alert('xss')</script>"
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': malicious_input
        }

        # Use format='json'
        response = self.client.post(reverse('api_contact'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        contact = Contact.objects.last()

        # Ensure raw malicious input is NOT stored (should be sanitized)
        self.assertNotEqual(contact.message, malicious_input)
        # Ensure sanitized version IS stored (default bleach behavior)
        self.assertIn("&lt;script&gt;", contact.message)
