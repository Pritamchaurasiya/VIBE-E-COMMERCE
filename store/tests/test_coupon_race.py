from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from store.models import Coupon
from store.coupon_service import CouponService

class CouponRaceConditionTest(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="RACE20",
            discount_type="percent",
            discount_value=Decimal("20"),
            valid_from=timezone.now(),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            max_uses=1,
            used_count=0,
            is_active=True,
            min_order_value=Decimal("0")
        )
        self.service = CouponService()

    def test_apply_coupon_increments_count(self):
        success, message = self.service.apply_coupon("RACE20")
        self.assertTrue(success)
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 1)

    def test_apply_coupon_enforces_limit(self):
        # Apply once - should succeed
        success, message = self.service.apply_coupon("RACE20")
        self.assertTrue(success)

        # Apply twice - should fail because max_uses is 1 and we have atomic check now.
        success, message = self.service.apply_coupon("RACE20")
        self.assertFalse(success)
        self.assertEqual(message, "Coupon usage limit reached")

        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 1)
