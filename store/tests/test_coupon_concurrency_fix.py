from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from store.models import Coupon
from store.coupon_service import CouponService

class CouponConcurrencyFixTest(TestCase):
    def setUp(self):
        self.service = CouponService()
        self.valid_coupon = Coupon.objects.create(
            code='RACE20',
            discount_type='percent',
            discount_value=Decimal('20.00'),
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True,
            max_uses=5,
            used_count=0
        )
        self.exhausted_coupon = Coupon.objects.create(
            code='FULL',
            discount_type='fixed',
            discount_value=Decimal('10.00'),
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=30),
            is_active=True,
            max_uses=5,
            used_count=5
        )

    def test_apply_coupon_increments_count(self):
        """Test that apply_coupon correctly increments the used_count."""
        initial_count = self.valid_coupon.used_count
        success, message = self.service.apply_coupon('RACE20')

        self.assertTrue(success)
        self.valid_coupon.refresh_from_db()
        self.assertEqual(self.valid_coupon.used_count, initial_count + 1)
        self.assertEqual(message, "Coupon applied successfully")

    def test_apply_exhausted_coupon_fails(self):
        """Test that apply_coupon fails if max_uses is reached."""
        initial_count = self.exhausted_coupon.used_count
        # Currently, the buggy implementation might allow this if it doesn't check limits in apply_coupon
        # But even if it doesn't explicitly check, the new implementation MUST ensure it fails.
        # The current implementation DOES NOT check usage limits in apply_coupon!
        # It blindly increments. So this test might actually FAIL (pass as in "it applies") on the current code
        # if I don't assert expected failure.

        # NOTE: The current code DOES increment even if full because it lacks the check.
        # So I expect this to fail initially (i.e., return True) before I fix it.
        # But I'm writing the test for the DESIRED behavior.

        success, message = self.service.apply_coupon('FULL')

        if success:
            print("WARNING: Bug reproduced - Applied exhausted coupon")
        else:
            print("Behavior correct - Rejected exhausted coupon")

        # After fix, these should be:
        self.assertFalse(success, "Should not apply exhausted coupon")
        self.exhausted_coupon.refresh_from_db()
        self.assertEqual(self.exhausted_coupon.used_count, initial_count, "Should not increment exhausted coupon")
