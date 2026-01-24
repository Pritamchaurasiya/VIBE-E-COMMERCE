from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class AgriFeaturesTests(APITestCase):
    def test_weather_api(self):
        """
        Ensure we can get weather data.
        """
        url = reverse('api_weather')
        response = self.client.get(url, {'city': 'Varanasi'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('current', response.data)
        self.assertIn('forecast', response.data)
        self.assertEqual(response.data['city'], 'Varanasi')

    def test_soil_health_api(self):
        """
        Ensure we can get soil health data.
        """
        url = reverse('api_soil_health')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('soil_health', response.data)
        self.assertIn('recommendations', response.data['soil_health'])

    def test_mandi_prices_api(self):
        """
        Ensure we can get mandi prices.
        """
        url = reverse('api_mandi_prices')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('prices', response.data)
        self.assertTrue(len(response.data['prices']) > 0)
