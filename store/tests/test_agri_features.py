from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from store.models import WeatherLog, SoilHealthReport, MandiPrice

class AgriFeaturesTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='agriuser', password='password')
        self.client.force_authenticate(user=self.user)

    def test_weather_endpoint(self):
        # Create dummy log
        WeatherLog.objects.create(city='Delhi', temperature=30.0, condition='Sunny')

        response = self.client.get(reverse('api_weather'), {'city': 'Delhi'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['temperature']), 30.0)

    def test_soil_health_endpoint(self):
        data = {
            'ph_level': 5.5,
            'nitrogen': 100,
            'phosphorus': 50,
            'potassium': 150,
            'organic_carbon': 0.5
        }
        response = self.client.post(reverse('api_soil_health'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('Acidic' in response.data['recommendation'])

        # Verify list
        response = self.client.get(reverse('api_soil_health'))
        # Handle pagination
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)

    def test_mandi_prices_endpoint(self):
        MandiPrice.objects.create(crop='Wheat', market='Azadpur', price=2000.00)

        response = self.client.get(reverse('api_mandi_prices'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle pagination
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['crop'], 'Wheat')

    def test_prediction_endpoint(self):
        # Create user interactions
        from store.models import UserInteraction, UserSession
        from django.utils import timezone

        session = UserSession.objects.create(
            user=self.user,
            session_id='test_session',
            is_active=True,
            last_activity=timezone.now()
        )

        UserInteraction.objects.create(
            user=self.user,
            session=session,
            interaction_type='add_to_cart',
            timestamp=timezone.now()
        )

        response = self.client.get(reverse('api_predict_purchase'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Base 0.1 + Active Session 0.2 + Cart Add 0.4 = 0.7
        self.assertGreaterEqual(float(response.data['purchase_probability']), 0.7)
        self.assertEqual(response.data['level'], 'High')

    def test_user_farm_endpoint(self):
        from store.models import UserFarm
        data = {
            'farm_name': 'Green Acres',
            'area_acres': 10.5,
            'primary_crop': 'Rice',
            'soil_type': 'Clay',
            'irrigation_type': 'Canal'
        }
        response = self.client.put(reverse('api_user_farm'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['farm_name'], 'Green Acres')

        # Verify persistence
        farm = UserFarm.objects.get(user=self.user)
        self.assertEqual(farm.primary_crop, 'Rice')
