from django.test import TestCase
from store.models import UserAnalyticsAPIKey
from store.serializers import UserAnalyticsAPIKeySerializer

class APIKeySecurityTest(TestCase):
    def test_secret_key_security(self):
        """
        Verify that the secret key is hashed and handled securely.
        """
        raw_secret = "secret_value_123"

        # 1. Test creation via serializer (simulating API usage)
        data = {
            "name": "Test Key",
            "api_key": "test_api_key",
            "secret_key": raw_secret,
            "permissions": {"read": True}
        }
        serializer = UserAnalyticsAPIKeySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        api_key = serializer.save()

        # Verify response contains plain_secret_key but NOT secret_key
        # Note: serializer.data accesses the saved instance
        response_data = serializer.data
        self.assertIn('plain_secret_key', response_data)
        self.assertEqual(response_data['plain_secret_key'], raw_secret)
        # secret_key is write_only, should not be in output
        self.assertNotIn('secret_key', response_data)

        # 2. Verify storage in DB
        api_key.refresh_from_db()
        self.assertNotEqual(api_key.secret_key, raw_secret)
        self.assertTrue(api_key.secret_key.startswith('pbkdf2_'))

        # 3. Verify verification method
        self.assertTrue(api_key.verify_secret(raw_secret))
        self.assertFalse(api_key.verify_secret("wrong_secret"))

        # 4. Verify retrieval via serializer (should NOT show plain key)
        # Fetch fresh from DB to simulate a new request
        fresh_api_key = UserAnalyticsAPIKey.objects.get(id=api_key.id)
        serializer_read = UserAnalyticsAPIKeySerializer(fresh_api_key)
        read_data = serializer_read.data
        self.assertIsNone(read_data['plain_secret_key'])
        self.assertNotIn('secret_key', read_data)
