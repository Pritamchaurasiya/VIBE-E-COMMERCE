from django.test import TestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService
from decimal import Decimal

class CouponRaceConditionTest(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="RACE10",
            discount_type="percent",
            discount_value=Decimal("10.00"),
            min_order_value=Decimal("100.00"),
            max_uses=5,
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )
        self.service = CouponService()

    def test_apply_coupon_success(self):
        """Test successful coupon application logic."""
        success, message = self.service.apply_coupon("RACE10")
        self.assertTrue(success)
        self.assertEqual(message, "Coupon applied successfully")

        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 1)

    def test_apply_coupon_max_uses(self):
        """Test logic respecting max_uses."""
        self.coupon.max_uses = 1
        self.coupon.save()

        # First application should succeed
        success, message = self.service.apply_coupon("RACE10")
        self.assertTrue(success)

        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 1)

        # Second application should fail
        success, message = self.service.apply_coupon("RACE10")
        self.assertFalse(success)
        self.assertEqual(message, "This coupon has reached its usage limit")

        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 1)

    def test_apply_coupon_increment(self):
        """Test that used_count increments correctly."""
        self.service.apply_coupon("RACE10")
        self.service.apply_coupon("RACE10")

        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 2)
