import threading
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from django.test import TransactionTestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService
from django.db import connections

class CouponRaceConditionTest(TransactionTestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code='RACE10',
            discount_type='fixed',
            discount_value=Decimal('10.00'),
            min_order_value=Decimal('0.00'),
            max_uses=1,  # Only 1 use allowed
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )
        self.service = CouponService()

    def test_race_condition(self):
        """
        Test that multiple threads attempting to apply the coupon simultaneously
        respect the max_uses limit.
        """
        success_count = 0
        lock = threading.Lock()

        def apply_coupon():
            nonlocal success_count
            # Create a new service instance or just call apply_coupon
            # We assume apply_coupon handles DB connections correctly (Django usually does thread locals)
            result, msg = self.service.apply_coupon('RACE10')
            if result:
                with lock:
                    success_count += 1
            connections.close_all() # Ensure connection is returned/closed

        num_threads = 5
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(apply_coupon) for _ in range(num_threads)]
            for f in futures:
                f.result()

        # Reload coupon
        self.coupon.refresh_from_db()

        print(f"Success count: {success_count}")
        print(f"Used count: {self.coupon.used_count}")

        # In a race condition, success_count might be > 1
        # We assert that success_count <= 1.
        self.assertLessEqual(success_count, 1, f"Race condition detected! {success_count} threads applied the coupon (max_uses=1).")
        self.assertEqual(self.coupon.used_count, success_count, "Used count does not match success count")
