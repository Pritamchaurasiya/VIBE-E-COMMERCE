from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from store.models import Order, User
from django.conf import settings
import json
import hashlib
import hmac

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class RazorpaySecurityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.order = Order.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            phone='1234567890',
            paid_amount=100.00,
            status='pending',
            payment_method='razorpay'
        )
        self.url = reverse('api_webhook', kwargs={'provider': 'razorpay'})
        self.payload = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_123456",
                        "notes": {
                            "order_id": self.order.id
                        }
                    }
                }
            }
        }

    def test_webhook_fails_when_secret_missing(self):
        """
        Fix Verification:
        If RAZORPAY_WEBHOOK_SECRET is not set, the request should fail with 500 error
        and the order should NOT be updated.
        """
        # Ensure secret is unset
        if hasattr(settings, 'RAZORPAY_WEBHOOK_SECRET'):
            delattr(settings, 'RAZORPAY_WEBHOOK_SECRET')

        # Send request WITHOUT signature header
        response = self.client.post(
            self.url,
            data=json.dumps(self.payload),
            content_type='application/json'
        )

        # EXPECTED BEHAVIOR: Returns 500 Server Error
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Verify order was NOT marked paid
        self.order.refresh_from_db()
        self.assertFalse(self.order.paid)

    def test_webhook_invalid_signature(self):
        # Set a dummy secret
        with self.settings(RAZORPAY_WEBHOOK_SECRET='test_secret'):
            # Send request with INVALID signature
            response = self.client.post(
                self.url,
                data=json.dumps(self.payload),
                content_type='application/json',
                HTTP_X_RAZORPAY_SIGNATURE='invalid_signature'
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_webhook_valid_signature(self):
        secret = 'test_secret'
        with self.settings(RAZORPAY_WEBHOOK_SECRET=secret):
            body = json.dumps(self.payload)
            signature = hmac.new(
                secret.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()

            response = self.client.post(
                self.url,
                data=body,
                content_type='application/json',
                HTTP_X_RAZORPAY_SIGNATURE=signature
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
