from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Profile, UserCoin
from rest_framework.test import APIClient

class ProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testprofile', email='test@example.com', first_name='Test', last_name='User')

        # Signal might have created profile, check and update or create
        if hasattr(self.user, 'profile'):
            self.profile = self.user.profile
            self.profile.shop_name = 'Test Shop'
            self.profile.city = 'Test City'
            self.profile.save()
        else:
            self.profile = Profile.objects.create(user=self.user, shop_name='Test Shop', city='Test City')

        # Ensure coins exist
        UserCoin.objects.get_or_create(user=self.user)

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_profile_completeness(self):
        url = reverse('api_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Fields filled: first_name, last_name, email, shop_name, city. (5 fields)
        # Total: 7.
        # Expected: int(5/7 * 100) = 71
        self.assertEqual(response.data['completeness'], 71)
