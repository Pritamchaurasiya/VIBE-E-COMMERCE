
import threading
from django.test import TransactionTestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService

class CouponConcurrencyTest(TransactionTestCase):
    def setUp(self):
        # Create a coupon with max_uses=1
        self.coupon = Coupon.objects.create(
            code="RACE10",
            discount_type="percent",
            discount_value=10,
            max_uses=1,
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )
        self.service = CouponService()

    def test_concurrent_usage(self):
        """
        Test that multiple threads attempting to use a coupon simultaneously
        respect the max_uses limit.
        """
        success_count = 0
        threads = []
        num_threads = 5

        def apply_coupon_wrapper():
            nonlocal success_count
            success, _ = self.service.apply_coupon("RACE10")
            if success:
                with threading.Lock():
                    success_count += 1

        for _ in range(num_threads):
            t = threading.Thread(target=apply_coupon_wrapper)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Refresh from DB
        self.coupon.refresh_from_db()

        # If strict consistency is enforced, only 1 should succeed.
        self.assertEqual(success_count, 1, f"Race condition detected! {success_count} threads succeeded, expected 1.")
        self.assertEqual(self.coupon.used_count, 1, f"Race condition detected! Coupon used {self.coupon.used_count} times, expected 1.")
