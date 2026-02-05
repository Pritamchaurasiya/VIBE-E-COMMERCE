from django.test import TransactionTestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService
import threading
from concurrent.futures import ThreadPoolExecutor

class CouponConcurrencyTest(TransactionTestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code='RACE100',
            discount_type='fixed',
            discount_value=10,
            max_uses=1000,  # High enough to allow all threads to succeed if counted correctly
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )

    def test_concurrent_coupon_usage(self):
        # We need enough concurrency to hit the race condition
        num_threads = 50

        def apply_coupon():
            service = CouponService()
            service.apply_coupon('RACE100')

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(apply_coupon) for _ in range(num_threads)]
            for future in futures:
                future.result()

        self.coupon.refresh_from_db()
        print(f"Expected used_count: {num_threads}, Actual used_count: {self.coupon.used_count}")

        # If race condition exists, actual used_count will be less than num_threads
        self.assertEqual(self.coupon.used_count, num_threads,
                         f"Race condition detected! Expected {num_threads}, got {self.coupon.used_count}")
