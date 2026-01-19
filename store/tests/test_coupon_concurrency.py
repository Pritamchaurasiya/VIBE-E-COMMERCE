from django.test import TransactionTestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService
import threading
from concurrent.futures import ThreadPoolExecutor

class CouponRaceConditionTest(TransactionTestCase):
    def setUp(self):
        self.coupon_code = "RACE10"
        self.max_uses = 5
        self.coupon = Coupon.objects.create(
            code=self.coupon_code,
            discount_type='percent',
            discount_value=10,
            max_uses=self.max_uses,
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )
        self.service = CouponService()

    def test_concurrent_coupon_application(self):
        """
        Test that applying coupon concurrently respects max_uses.
        Without atomic updates, this is expected to fail (allow more uses).
        """
        num_threads = 20  # Try to apply 20 times, limit is 5

        def apply_coupon():
            return self.service.apply_coupon(self.coupon_code)

        results = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(apply_coupon) for _ in range(num_threads)]
            for future in futures:
                results.append(future.result())

        # Reload coupon from DB
        self.coupon.refresh_from_db()

        success_count = sum(1 for success, msg in results if success)

        print(f"\nAttempts: {num_threads}")
        print(f"Max uses: {self.max_uses}")
        print(f"Successful applications: {success_count}")
        print(f"Final used_count in DB: {self.coupon.used_count}")

        # In a race condition, success_count might be > max_uses
        # Or used_count might be < success_count (lost updates)

        # We want to assert that we strictly enforce the limit
        self.assertLessEqual(success_count, self.max_uses, f"Race condition detected! Allowed {success_count} uses for limit {self.max_uses}")
        self.assertEqual(self.coupon.used_count, success_count, "DB count mismatch with success count")
