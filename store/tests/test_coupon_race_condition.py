from django.test import TransactionTestCase
from django.contrib.auth.models import User
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService
import threading
from datetime import timedelta
from decimal import Decimal

class CouponRaceConditionTest(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.coupon = Coupon.objects.create(
            code='RACE10',
            discount_type='fixed',
            discount_value=Decimal('10.00'),
            min_order_value=Decimal('0.00'),
            max_uses=5,
            used_count=0,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            is_active=True
        )

    def test_concurrent_apply_coupon(self):
        """
        Test that concurrent coupon applications do not exceed max_uses
        and maintain data consistency.
        """
        threads = []
        success_count = 0
        lock = threading.Lock()

        def apply():
            nonlocal success_count
            # Use a fresh connection/service per thread logic if needed,
            # but Django handles thread-locals for connections.
            svc = CouponService(self.user)
            success, _ = svc.apply_coupon('RACE10')
            if success:
                with lock:
                    success_count += 1

        # Launch 20 threads for a coupon with 5 max uses
        for _ in range(20):
            t = threading.Thread(target=apply)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.coupon.refresh_from_db()
        print(f"\nResults - Successes: {success_count}, DB Used Count: {self.coupon.used_count}")

        # FAIL condition 1: More successful applications than allowed
        self.assertLessEqual(success_count, 5, f"Race condition detected! Coupon used {success_count} times, max allowed 5")

        # FAIL condition 2: DB count doesn't match successful applications
        self.assertEqual(success_count, self.coupon.used_count, f"Data inconsistency! Successes: {success_count}, DB count: {self.coupon.used_count}")
