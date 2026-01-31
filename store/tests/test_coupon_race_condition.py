import threading
from django.test import TransactionTestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService

class CouponRaceConditionTest(TransactionTestCase):
    def setUp(self):
        self.coupon_code = "RACE20"
        self.coupon = Coupon.objects.create(
            code=self.coupon_code,
            discount_type='percent',
            discount_value=10,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            max_uses=20,
            used_count=0,
            is_active=True
        )
        self.service = CouponService()

    def test_concurrent_usage(self):
        def apply_coupon():
            self.service.apply_coupon(self.coupon_code)

        threads = []
        for _ in range(20):
            t = threading.Thread(target=apply_coupon)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.coupon.refresh_from_db()
        # Without fix, race condition will cause used_count < 20
        self.assertEqual(self.coupon.used_count, 20,
                         f"Race condition detected! Expected 20, got {self.coupon.used_count}")
