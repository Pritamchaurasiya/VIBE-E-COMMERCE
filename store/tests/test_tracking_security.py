import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from store.models import OTPVerification
from django.utils import timezone
from datetime import timedelta
from django.test import override_settings, TransactionTestCase
from store.tracking_service import InputValidator, RateLimiter

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    AXES_ENABLED=False
)
class TestTrackingSecurity(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_send_otp(self):
        url = reverse('api_send_otp')
        data = {'phone': '1234567890'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('debug_otp', response.data)

        # Verify DB record
        self.assertTrue(OTPVerification.objects.filter(phone='1234567890').exists())

    def test_verify_otp_success(self):
        # Create OTP
        otp_code = '123456'
        OTPVerification.objects.create(
            phone='1234567890',
            otp=otp_code,
            purpose='login',
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = reverse('api_verify_otp')
        data = {'phone': '1234567890', 'otp': otp_code, 'purpose': 'login'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        # Check verified status
        self.assertTrue(OTPVerification.objects.get(phone='1234567890').is_verified)

    def test_verify_otp_failure(self):
        # Create OTP
        otp_code = '123456'
        OTPVerification.objects.create(
            phone='1234567890',
            otp=otp_code,
            purpose='login',
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = reverse('api_verify_otp')
        data = {'phone': '1234567890', 'otp': '000000', 'purpose': 'login'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check attempts incremented
        self.assertEqual(OTPVerification.objects.get(phone='1234567890').attempts, 1)

    def test_input_validator(self):
        # Test SQL injection detection
        self.assertTrue(InputValidator.detect_sql_injection("SELECT * FROM users"))
        self.assertFalse(InputValidator.detect_sql_injection("Safe string"))

        # Test XSS detection
        self.assertTrue(InputValidator.detect_xss("<script>alert('xss')</script>"))
        self.assertFalse(InputValidator.detect_xss("Safe string"))

    def test_rate_limiter(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        identifier = "test_user"

        self.assertTrue(limiter.is_allowed(identifier))
        self.assertTrue(limiter.is_allowed(identifier))
        self.assertFalse(limiter.is_allowed(identifier))
