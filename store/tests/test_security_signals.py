from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.signals import user_logged_in
from store.models import Notification, UserSession

class SecuritySignalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='security_user', password='password')
        self.factory = RequestFactory()

    def test_new_device_notification(self):
        """Test that logging in with a new User-Agent creates a notification."""
        request = self.factory.post('/login')
        request.user = self.user
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (New Device)'

        # Manually trigger signal as logging in via factory doesn't always trigger it fully in test env without session
        user_logged_in.send(sender=User, user=self.user, request=request)

        # Check notification
        self.assertTrue(Notification.objects.filter(user=self.user, title='New Login Detected').exists())

    def test_known_device_no_notification(self):
        """Test that logging in with known device does NOT create notification."""
        # Create a session for this user agent
        UserSession.objects.create(
            user=self.user,
            session_id='test_session',
            user_agent='Mozilla/5.0 (Known Device)',
            ip_address='127.0.0.1'
        )

        request = self.factory.post('/login')
        request.user = self.user
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Known Device)'

        # Clear existing notifications
        Notification.objects.all().delete()

        user_logged_in.send(sender=User, user=self.user, request=request)

        self.assertFalse(Notification.objects.filter(user=self.user, title='New Login Detected').exists())
