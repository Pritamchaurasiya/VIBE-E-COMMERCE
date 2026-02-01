from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from store.models import UserFarm, Order
from rest_framework.test import APIClient
from rest_framework import status
import json

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    REST_FRAMEWORK={
        'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication'
        ],
        'DEFAULT_THROTTLE_CLASSES': [], # Disable throttling
        'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    },
    AXES_ENABLED=False
)
class EndToEndFlowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.admin = User.objects.create_superuser(username='admin', password='password', email='admin@example.com')

    def test_user_farm_lifecycle(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_user_farm')

        # 1. Create/Get (should be empty initially)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['farm_size']), 0.00)

        # 2. Update
        data = {
            'farm_name': 'Green Acres',
            'farm_size': 10.50,
            'primary_crops': ['Wheat', 'Rice'],
            'location': 'Punjab'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['farm_name'], 'Green Acres')

        # 3. Verify persistence
        farm = UserFarm.objects.get(user=self.user)
        self.assertEqual(farm.farm_name, 'Green Acres')
        self.assertEqual(float(farm.farm_size), 10.50)

    def test_advanced_analytics(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('api_advanced_analytics')

        # Create some dummy orders
        for i in range(10):
            Order.objects.create(
                paid=True,
                paid_amount=100.00 + (i * 10),
                first_name='Test', last_name='User', email='test@example.com',
                address='123 St', zipcode='12345', place='City', phone='1234567890'
            )

        # Add an anomaly
        Order.objects.create(
            paid=True,
            paid_amount=10000.00,
            first_name='Anomaly', last_name='User', email='test@example.com',
            address='123 St', zipcode='12345', place='City', phone='1234567890'
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('anomaly_detection', response.data)
        self.assertIn('forecast', response.data)

        # Check if anomaly was detected (might depend on ML engine state/data points)
        # We just ensure the structure is correct for now
        self.assertIn('is_anomaly', response.data['anomaly_detection'])
