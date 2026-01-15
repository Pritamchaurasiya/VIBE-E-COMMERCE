from django.test import TestCase
from store.models import UserAnalyticsAPIKey
from store.serializers import UserAnalyticsAPIKeySerializer

class UserAnalyticsAPIKeySerializerTest(TestCase):
    def test_secret_key_not_exposed(self):
        """
        Test that secret_key is not exposed in the serializer output.
        """
        api_key = UserAnalyticsAPIKey.objects.create(
            name="Test Key",
            api_key="pk_test_12345",
            secret_key="sk_test_SECRET",
            permissions={"read": True}
        )

        serializer = UserAnalyticsAPIKeySerializer(api_key)
        data = serializer.data

        self.assertNotIn('secret_key', data)
        self.assertEqual(data['api_key'], "pk_test_12345")
