from django.test import TestCase, override_settings
from django.urls import reverse
from django.conf import settings
import json

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    # Also disable throttling for tests to avoid other cache issues if any
    REST_FRAMEWORK={
        'DEFAULT_PERMISSION_CLASSES': [
             'rest_framework.permissions.AllowAny',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_THROTTLE_CLASSES': [],
    }
)
class RazorpayWebhookSecurityTest(TestCase):
    def test_missing_secret_fails_securely(self):
        """
        If RAZORPAY_WEBHOOK_SECRET is not configured, the webhook should NOT be processed.
        It should return 500 or 403, but definitely not 200.
        """
        # We simulate the setting being empty
        with override_settings(RAZORPAY_WEBHOOK_SECRET=''):
            # Simulate a webhook request
            payload = {
                'event': 'payment.captured',
                'payload': {
                    'payment': {'entity': {'id': 'pay_123', 'notes': {'order_id': 1}}}
                }
            }
            # We send a signature, but since secret is empty, the view currently
            # might skip verification and process it.
            headers = {
                'HTTP_X_RAZORPAY_SIGNATURE': 'fake_signature',
                'CONTENT_TYPE': 'application/json'
            }

            # Using client.post with content_type to ensure it's treated as JSON
            response = self.client.post(
                reverse('api_webhook', kwargs={'provider': 'razorpay'}),
                data=payload,
                content_type='application/json',
                **headers
            )

            # Currently it fails open (returns 200) because verification is skipped.
            # We assert that this is NOT 200 (proving the vulnerability exists if it fails this assertion).

            self.assertNotEqual(response.status_code, 200, "CRITICAL: Webhook processed despite missing secret! Signature verification was bypassed.")
