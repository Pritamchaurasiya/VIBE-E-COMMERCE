from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from store.models import Equipment, Vendor, GovernmentScheme, ForumPost, RentalBooking
from datetime import date, timedelta

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class NewFeaturesTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.vendor_user = User.objects.create_user(username='vendoruser', password='password')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', created_by=self.vendor_user, city='Varanasi')

        self.equipment = Equipment.objects.create(
            name='Tractor',
            slug='tractor',
            description='Heavy duty',
            vendor=self.vendor,
            daily_rate=1000,
            location='Varanasi'
        )

        self.scheme = GovernmentScheme.objects.create(
            title='PM Kisan',
            slug='pm-kisan',
            description='Income support',
            eligibility='Small farmers',
            benefits='6000 per year',
            state='All India'
        )

    def test_get_equipment_list(self):
        response = self.client.get('/api/v1/equipment/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check structure (DRF pagination might return 'results')
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

    def test_create_rental_booking(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'equipment_id': self.equipment.id,
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=2))
        }
        response = self.client.post('/api/v1/rentals/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RentalBooking.objects.count(), 1)
        booking = RentalBooking.objects.first()
        self.assertEqual(booking.total_cost, 2000)

    def test_get_schemes(self):
        response = self.client.get('/api/v1/schemes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_forum_post(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Best crop for Rabi?',
            'content': 'Please suggest.'
        }
        response = self.client.post('/api/v1/forum/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ForumPost.objects.count(), 1)

    def test_agribot(self):
        response = self.client.post('/api/v1/chat/', {'message': 'wheat price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('2125', response.data['response'])
