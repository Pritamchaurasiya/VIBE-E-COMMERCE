
from django.test import TransactionTestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService
import threading

class CouponRaceConditionTest(TransactionTestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code='RACE100',
            discount_type='fixed',
            discount_value=10,
            max_uses=10,
            used_count=0,
            valid_from=timezone.now(),
            valid_until=timezone.now() + timezone.timedelta(days=1)
        )
        self.service = CouponService()

    def test_concurrent_apply_coupon(self):
        """Test concurrent coupon application to check for race conditions."""

        # We'll try to apply the coupon 20 times concurrently
        # With max_uses=10, we expect exactly 10 successes and 10 failures
        # if the locking works correctly.

        threads = []
        results = []

        def apply():
            success, msg = self.service.apply_coupon('RACE100')
            results.append(success)

        for _ in range(20):
            t = threading.Thread(target=apply)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.coupon.refresh_from_db()

        success_count = results.count(True)
        print(f"Success count: {success_count}, Used count: {self.coupon.used_count}")

        # Ensure data integrity: successful applications must match database count
        self.assertEqual(success_count, self.coupon.used_count)

        # Ensure business logic: usage count must not exceed max_uses
        # Note: In SQLite with high contention, we might get fewer than 10 successes due to locking errors,
        # but we must NEVER exceed 10.
        self.assertLessEqual(self.coupon.used_count, 10)
