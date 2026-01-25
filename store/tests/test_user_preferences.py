from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from store.models import UserPreference, Profile

class UserProfileAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='prefuser', password='password')
        self.client.force_authenticate(user=self.user)
        # Profile is created by signal

    def test_update_preferences(self):
        data = {
            'preferences': {
                'theme_mode': 'dark',
                'dashboard_layout': 'compact'
            }
        }
        response = self.client.put('/api/v1/profile/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(UserPreference.objects.filter(user=self.user, preference_key='theme_mode', preference_value='dark').exists())
        self.assertTrue(UserPreference.objects.filter(user=self.user, preference_key='dashboard_layout', preference_value='compact').exists())
