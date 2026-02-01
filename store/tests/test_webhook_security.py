"""
Security tests for Webhook endpoints.
"""
import hmac
import hashlib
import json
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class RazorpayWebhookSecurityTest(TestCase):
    """Test security of Razorpay webhook endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api_webhook', kwargs={'provider': 'razorpay'})
        self.payload = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_1234567890',
                        'amount': 1000,
                        'currency': 'INR',
                        'notes': {
                            'order_id': 1
                        }
                    }
                }
            }
        }
        self.json_payload = json.dumps(self.payload)

    @override_settings(RAZORPAY_WEBHOOK_SECRET='')
    def test_webhook_rejected_without_secret(self):
        """
        Test that webhook is rejected with 500 Error when RAZORPAY_WEBHOOK_SECRET
        is not configured, preventing signature bypass.
        """
        # Send request without signature header
        response = self.client.post(
            self.url,
            data=self.payload,
            format='json'
        )

        # Should return 500 Internal Server Error (Configuration Error)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @override_settings(RAZORPAY_WEBHOOK_SECRET='test_secret')
    def test_webhook_rejected_with_invalid_signature(self):
        """Test that webhook is rejected when secret is set but signature is invalid."""
        response = self.client.post(
            self.url,
            data=self.payload,
            format='json',
            HTTP_X_RAZORPAY_SIGNATURE='invalid_signature'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(RAZORPAY_WEBHOOK_SECRET='test_secret')
    def test_webhook_accepted_with_valid_signature(self):
        """Test that webhook is accepted with valid signature."""
        # Use exact JSON string to ensure signature matches
        data = json.dumps(self.payload)
        signature = hmac.new(
            b'test_secret',
            data.encode(),
            hashlib.sha256
        ).hexdigest()

        response = self.client.post(
            self.url,
            data=data,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=signature
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
