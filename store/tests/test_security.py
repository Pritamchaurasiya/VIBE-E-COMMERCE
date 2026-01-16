from django.test import TestCase
from django.test.client import Client

class SecurityMiddlewareTest(TestCase):
    def test_security_headers(self):
        client = Client()
        # Using a URL that likely exists or 404, headers should be present regardless
        response = client.get('/api/v1/health/')

        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.headers.get('X-XSS-Protection'), '1; mode=block')
        self.assertEqual(response.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
