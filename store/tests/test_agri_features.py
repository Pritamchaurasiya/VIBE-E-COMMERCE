from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

@override_settings(
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ],
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class AgriFeaturesTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='agriuser', password='password')
        self.client.force_authenticate(user=self.user)

    def test_user_farm_profile(self):
        url = reverse('api_user_farm')
        data = {
            'farm_size': 10.5,
            'soil_type': 'loamy',
            'irrigation_type': 'drip',
            'primary_crops': ['Wheat', 'Rice']
        }

        # Create/Update (PUT creates if get_or_create is used in view's get_object,
        # but standard UpdateAPIView expects an object to exist or we need to handle creation.
        # However, I used get_or_create in get_object, so it should exist.)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['farm_size']), 10.5)

        # Retrieve
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['soil_type'], 'loamy')

    def test_disease_diagnosis(self):
        url = reverse('api_disease_diagnosis')
        image = SimpleUploadedFile("leaf.jpg", b"file_content", content_type="image/jpeg")
        data = {'image': image}

        # Unauthenticated request (should be allowed)
        self.client.logout()
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('diagnosis', response.data)
        self.assertIn('recommendations', response.data)

    def test_purchase_prediction(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_purchase_prediction')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('predicted_category', response.data)
        self.assertIn('predicted_date', response.data)
