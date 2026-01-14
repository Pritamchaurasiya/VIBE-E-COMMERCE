from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from store.models import ForumPost, MarketPrice, Crop

class NewFeaturesAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.crop = Crop.objects.create(name='Wheat', slug='wheat')

    def test_market_prices(self):
        MarketPrice.objects.create(
            crop=self.crop, market_name='Delhi Mandi', location='Delhi',
            price=2000.00, date='2023-10-27'
        )
        response = self.client.get(reverse('api_market_prices'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle pagination
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_forum_posts(self):
        ForumPost.objects.create(
            author=self.user, title='Test Post', content='Content'
        )
        response = self.client.get(reverse('api_forum_posts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle pagination
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_create_forum_post(self):
        self.client.force_authenticate(user=self.user)
        data = {'title': 'New Post', 'content': 'New Content', 'category': 'general'}
        response = self.client.post(reverse('api_forum_posts'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_disease_diagnosis(self):
        # We need to mock the image upload or send a file
        from django.core.files.uploadedfile import SimpleUploadedFile
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('api_disease_diagnosis'), {'image': image}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('disease', response.data)
