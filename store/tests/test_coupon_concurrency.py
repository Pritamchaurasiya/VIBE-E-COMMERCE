from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService

class CouponConcurrencyTest(TestCase):
    def setUp(self):
        self.service = CouponService()
        self.coupon = Coupon.objects.create(
            code='RACE100',
            discount_type='percent',
            discount_value=Decimal('10.00'),
            valid_from=timezone.now(),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            max_uses=2,
            used_count=0,
            is_active=True
        )

    def test_apply_coupon_success(self):
        """Test normal application of coupon."""
        success, msg = self.service.apply_coupon('RACE100')
        self.assertTrue(success)
        self.assertEqual(msg, "Coupon applied successfully")

        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 1)

    def test_apply_coupon_limit_reached(self):
        """Test application fails when limit reached."""
        self.coupon.used_count = 2
        self.coupon.save()

        success, msg = self.service.apply_coupon('RACE100')

        self.assertFalse(success)
        self.assertEqual(msg, "Coupon usage limit reached")

        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, 2)
