
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from store.models import UserActionTracker
from store.analytics_engine import analytics_engine
from datetime import timedelta

class AnalyticsEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='analytics_user', password='password')

    def test_predict_user_behavior_optimization(self):
        """Test that predict_user_behavior returns correct aggregated data."""
        # Create some user actions
        now = timezone.now()

        # Create 5 page_view actions
        for _ in range(5):
            UserActionTracker.objects.create(
                user=self.user,
                action_type='page_view',
                action_timestamp=now
            )

        # Create 3 purchase actions
        for _ in range(3):
            UserActionTracker.objects.create(
                user=self.user,
                action_type='purchase',
                action_timestamp=now
            )

        # Create actions for different days/hours would require mocking time
        # or manually setting action_timestamp (which I did above).
        # To test hourly/daily breakdown, I should vary timestamps.

        yesterday = now - timedelta(days=1)
        UserActionTracker.objects.create(
            user=self.user,
            action_type='login',
            action_timestamp=yesterday
        )

        # Run prediction
        # Use a longer window to ensure we cover the data
        result = analytics_engine.predictive_analytics.predict_user_behavior(self.user.id, days=7)

        # Verify structure
        self.assertIn('predicted_daily_actions', result)
        self.assertIn('most_active_days', result)
        self.assertIn('peak_activity_hours', result)
        self.assertIn('preferred_actions', result)

        # Verify aggregation correctness
        actions = result['preferred_actions']
        self.assertEqual(actions.get('page_view'), 5)
        self.assertEqual(actions.get('purchase'), 3)
        self.assertEqual(actions.get('login'), 1)

        # Verify total calculation logic implicitly via preferred_actions
        # Total = 5+3+1 = 9
        # Engagement score logic check (9 actions over 7 days)

    def test_predict_user_behavior_no_data(self):
        result = analytics_engine.predictive_analytics.predict_user_behavior(self.user.id)
        self.assertIn('error', result)
