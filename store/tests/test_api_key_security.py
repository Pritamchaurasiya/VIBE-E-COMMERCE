"""
Tests for UserAnalyticsAPIKey security.
"""
from django.test import TestCase
from store.models import UserAnalyticsAPIKey
from store.serializers import UserAnalyticsAPIKeySerializer
from django.contrib.auth.hashers import check_password

class UserAnalyticsAPIKeySecurityTests(TestCase):
    def test_create_api_key_hashes_secret(self):
        """Test that creating an API key hashes the secret key."""
        data = {
            'name': 'Test Secure Key',
            'permissions': {'read': True}
        }
        serializer = UserAnalyticsAPIKeySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()

        # Check plain_secret_key is available on creation
        self.assertTrue(hasattr(instance, 'plain_secret_key'))
        raw_key = instance.plain_secret_key
        self.assertIsNotNone(raw_key)

        # Check secret_key in DB is hashed
        db_instance = UserAnalyticsAPIKey.objects.get(id=instance.id)
        self.assertNotEqual(db_instance.secret_key, raw_key)
        self.assertTrue(check_password(raw_key, db_instance.secret_key))

    def test_plain_secret_key_not_stored(self):
        """Test that plain secret key is not stored/retrievable later."""
        data = {
            'name': 'Test Key 2',
            'permissions': {'read': True}
        }
        serializer = UserAnalyticsAPIKeySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()

        # Fetch fresh from DB
        db_instance = UserAnalyticsAPIKey.objects.get(id=instance.id)

        # Should not have plain_secret_key attribute
        self.assertFalse(hasattr(db_instance, 'plain_secret_key'))

        # Serializer should not expose secret_key or plain_secret_key on read
        read_serializer = UserAnalyticsAPIKeySerializer(instance=db_instance)
        self.assertNotIn('plain_secret_key', read_serializer.data)
        self.assertNotIn('secret_key', read_serializer.data)

    def test_verify_secret_key_method(self):
        """Test the model's verification method."""
        instance = UserAnalyticsAPIKey(name="Verify Test", permissions={})
        instance.save()
        instance.set_secret_key("my-secret-password")
        instance.save()

        self.assertTrue(instance.verify_secret_key("my-secret-password"))
        self.assertFalse(instance.verify_secret_key("wrong-password"))

    def test_legacy_key_upgrade(self):
        """Test that legacy plaintext keys are auto-upgraded."""
        instance = UserAnalyticsAPIKey(name="Legacy Test", permissions={})
        instance.secret_key = "plaintext-secret"  # Simulate legacy
        instance.save()

        # Verify works
        self.assertTrue(instance.verify_secret_key("plaintext-secret"))

        # Check if upgraded
        instance.refresh_from_db()
        self.assertNotEqual(instance.secret_key, "plaintext-secret")
        self.assertTrue(check_password("plaintext-secret", instance.secret_key))
