from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from store.models import UserFarm, SoilHealthReport, MandiPrice, Crop
from datetime import date

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    MIDDLEWARE=[
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]
)
class AgriFeaturesTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='farmer', password='password123')
        self.client.force_authenticate(user=self.user)

        # Create some crops
        self.crop = Crop.objects.create(name="Wheat", slug="wheat")

    def test_create_farm(self):
        """Test creating a farm."""
        data = {
            "name": "My Big Farm",
            "location": "Punjab",
            "size_acres": 10.5,
            "soil_type": "alluvial",
            "irrigation_source": "canal"
        }
        response = self.client.post('/api/v1/farms/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserFarm.objects.count(), 1)
        self.assertEqual(UserFarm.objects.get().name, "My Big Farm")

    def test_soil_report_recommendations(self):
        """Test that soil report generates recommendations."""
        farm = UserFarm.objects.create(
            user=self.user, name="Test Farm", size_acres=5, location="Test"
        )
        data = {
            "farm": farm.id,
            "sample_date": "2023-10-01",
            "ph_level": 5.5,  # Acidic -> Lime recommendation
            "nitrogen": 200,  # Low -> Nitrogen recommendation
            "phosphorus": 50,
            "potassium": 200
        }
        response = self.client.post('/api/v1/soil-health/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        report = SoilHealthReport.objects.get()
        self.assertIn("Nitrogen is low", report.recommendations)
        self.assertIn("Soil is acidic", report.recommendations)

    def test_mandi_prices(self):
        """Test fetching mandi prices."""
        MandiPrice.objects.create(
            state="Punjab", district="Ludhiana", market="Ludhiana",
            commodity="Wheat", arrival_date=date.today(),
            min_price=2000, max_price=2200, modal_price=2100
        )

        self.client.logout() # Public endpoint
        response = self.client.get('/api/v1/mandi-prices/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF pagination returns a dict with 'results'
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['market'], "Ludhiana")
