import threading
from django.test import TransactionTestCase
from store.models import Coupon
from store.coupon_service import CouponService
from django.utils import timezone
import time

class CouponRaceConditionTest(TransactionTestCase):
    def test_concurrent_coupon_usage(self):
        coupon = Coupon.objects.create(
            code="RACE10",
            discount_type="percent",
            discount_value=10,
            max_uses=5,
            used_count=0,
            valid_from=timezone.now(),
            valid_until=timezone.now() + timezone.timedelta(days=1)
        )

        service = CouponService()

        def use_coupon():
            # Add a small delay to increase chance of race condition
            # Reading the coupon inside apply_coupon happens here
            # Then writing happens after
            service.apply_coupon("RACE10")

        threads = []
        # Try to launch more threads than the limit to force over-usage
        for _ in range(10):
            t = threading.Thread(target=use_coupon)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        coupon.refresh_from_db()
        print(f"Coupon used count: {coupon.used_count}")
        self.assertLessEqual(coupon.used_count, 5, f"Coupon used count {coupon.used_count} exceeded max_uses 5")
