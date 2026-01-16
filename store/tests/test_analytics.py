from django.test import TestCase
from django.urls import reverse
from store.models import AnalyticsEvent
from rest_framework.test import APIClient

class AnalyticsTest(TestCase):
    def test_search_analytics(self):
        client = APIClient()
        url = reverse('api_products')

        # Perform search
        client.get(url, {'q': 'test_query'})

        # Check if event was logged
        self.assertTrue(AnalyticsEvent.objects.filter(event_type='search').exists())
        event = AnalyticsEvent.objects.filter(event_type='search').first()
        self.assertEqual(event.data['query'], 'test_query')
