from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from store.models import Profile, UserCoin, Vendor, Product, Category, Order

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class NewFeaturesTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        # Profile and UserCoin are created via signals
        self.profile = self.user.profile
        self.user_coin = self.user.coins
        self.user_coin.balance = 100
        self.user_coin.save()
        self.client.force_authenticate(user=self.user)

    def test_weather_api(self):
        url = reverse('api_weather')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('location', response.data)
        self.assertIn('current', response.data)

    def test_soil_health_api(self):
        url = reverse('api_soil_health')
        data = {'n': 40, 'p': 10, 'k': 80, 'ph': 5.5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommendations', response.data)
        # Check low N logic
        analysis_str = " ".join(response.data['analysis'])
        self.assertIn("Nitrogen (N) is Low", analysis_str)

    def test_user_coins_profile(self):
        url = reverse('api_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['coin_balance'], 100)

    def test_vendor_analytics_access(self):
        # Regular user should not access
        url = reverse('api_vendor_analytics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Make user a vendor
        Vendor.objects.create(name="Test Vendor", slug="test-vendor", created_by=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('daily_sales', response.data)
