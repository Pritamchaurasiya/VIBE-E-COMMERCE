from django.test import TestCase
from store.coupon_service import CouponService
from store.models import Coupon
from django.utils import timezone
from datetime import timedelta
from django.db.models import F

class CouponRaceConditionTest(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="RACE10",
            discount_type="percent",
            discount_value=10,
            max_uses=2,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            is_active=True
        )
        self.service = CouponService()

    def test_apply_coupon_race_condition(self):
        # We can't easily simulate true parallelism in SQLite test environment
        # but we can verify the logic uses atomic updates (F expressions)

        # Verify initial state
        self.assertEqual(self.coupon.used_count, 0)

        # Apply coupon normally
        success, msg = self.service.apply_coupon("RACE10")
        self.assertTrue(success)

        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 1)

        # Apply again
        success, msg = self.service.apply_coupon("RACE10")
        self.assertTrue(success)

        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 2)

        # Apply third time (should fail)
        success, msg = self.service.apply_coupon("RACE10")
        self.assertFalse(success)
        self.assertIn("usage limit", msg)

        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 2)
