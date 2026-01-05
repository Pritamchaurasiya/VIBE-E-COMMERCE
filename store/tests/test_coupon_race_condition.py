from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from store.models import Coupon
from store.coupon_service import CouponService
from django.db.models import F

class CouponRaceConditionTest(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="RACE20",
            discount_type="percent",
            discount_value=20,
            min_order_value=100,
            max_uses=1000,
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )
        self.service = CouponService()

    def test_apply_coupon_atomic_increment(self):
        # Initial check
        self.assertEqual(self.coupon.used_count, 0)

        # Apply coupon
        success, message = self.service.apply_coupon("RACE20")

        self.assertTrue(success)
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 1)

    def test_validate_coupon_race_condition_logic(self):
        # This test ensures that even if we can't easily simulate concurrent requests,
        # the validation logic checks against the current DB state.

        # Set usage to max
        self.coupon.used_count = self.coupon.max_uses
        self.coupon.save()

        result = self.service.validate_coupon("RACE20", Decimal("200"))
        self.assertFalse(result.valid)
        self.assertEqual(result.error_message, "This coupon has reached its usage limit")
