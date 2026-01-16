from django.test import TestCase, override_settings
from django.test.client import Client

@override_settings(DEBUG=True)
class LoggingMiddlewareTest(TestCase):
    def test_request_duration_header(self):
        client = Client()
        response = client.get('/api/v1/health/')
        self.assertTrue(response.headers.get('X-Request-Duration'))
