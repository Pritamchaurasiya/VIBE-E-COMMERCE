from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

@override_settings(AXES_ENABLED=False)
class DiseaseDetectionAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api_disease_detection')

    def test_detect_disease_no_image(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_detect_disease_success(self):
        image = SimpleUploadedFile(
            "leaf.jpg", b"file_content", content_type="image/jpeg"
        )
        response = self.client.post(
            self.url,
            {'image': image, 'crop_type': 'wheat'},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('disease', response.data)
