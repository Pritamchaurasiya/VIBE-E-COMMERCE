
import json
import hmac
import hashlib
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Order, Product, OrderItem, Vendor, Category

class WebhookSecurityTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')

        # Create dependencies for Order
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=100.00,
            category=self.category,
            vendor=self.vendor
        )

        # Create an unpaid order
        self.order = Order.objects.create(
            user=self.user,
            paid_amount=100.00,
            paid=False,
            payment_method='razorpay',
            status='pending'
        )
        OrderItem.objects.create(order=self.order, product=self.product, price=100.00, quantity=1, vendor=self.vendor)

    @override_settings(RAZORPAY_WEBHOOK_SECRET='')
    def test_razorpay_webhook_no_secret_security(self):
        """
        Test that without a webhook secret, the endpoint rejects the request.
        This confirms the fix for the vulnerability.
        """
        payload = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_123456',
                        'notes': {
                            'order_id': self.order.id
                        }
                    }
                }
            }
        }

        # In the secure version, this should fail (500 Internal Server Error)
        response = self.client.post(
            reverse('api_webhook', kwargs={'provider': 'razorpay'}),
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check that order is NOT marked as paid
        self.order.refresh_from_db()
        self.assertFalse(self.order.paid, "Security confirmed: Order not paid without secret configuration")

    @override_settings(RAZORPAY_WEBHOOK_SECRET='test_secret')
    def test_razorpay_webhook_with_secret_verification(self):
        """
        Test that with a secret, signature verification works.
        """
        payload = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_123456',
                        'notes': {
                            'order_id': self.order.id
                        }
                    }
                }
            }
        }

        body = json.dumps(payload)
        secret = 'test_secret'
        signature = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()

        response = self.client.post(
            reverse('api_webhook', kwargs={'provider': 'razorpay'}),
            data=body,
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE=signature
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertTrue(self.order.paid)

    @override_settings(RAZORPAY_WEBHOOK_SECRET='test_secret')
    def test_razorpay_webhook_invalid_signature(self):
        """
        Test that with a secret, invalid signature is rejected.
        """
        payload = {'event': 'payment.captured'}
        response = self.client.post(
            reverse('api_webhook', kwargs={'provider': 'razorpay'}),
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_X_RAZORPAY_SIGNATURE='invalid_signature'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
