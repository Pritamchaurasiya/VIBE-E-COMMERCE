from django.test import TransactionTestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService
import threading
from datetime import timedelta
import time

class CouponRaceConditionTest(TransactionTestCase):
    def test_concurrent_coupon_application(self):
        # Create a coupon with max_uses=100 (enough to not hit limit)
        coupon = Coupon.objects.create(
            code="RACE20",
            discount_type="percent",
            discount_value=20,
            max_uses=100,
            used_count=0,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            is_active=True
        )

        success_count = 0
        lock = threading.Lock()

        def worker():
            nonlocal success_count
            service = CouponService()
            # Simple retry logic for SQLite locking
            for _ in range(5):
                try:
                    success, _ = service.apply_coupon("RACE20")
                    if success:
                        with lock:
                            success_count += 1
                    break
                except Exception:
                    time.sleep(0.1)

        threads = []
        for _ in range(10):  # Reduced threads to minimize locking errors
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        coupon.refresh_from_db()

        print(f"Threads reporting success: {success_count}")
        print(f"DB used_count: {coupon.used_count}")

        # If race condition exists, db_count < success_count
        # With fix, they should be equal
        self.assertEqual(coupon.used_count, success_count,
                         f"Race condition detected! DB count {coupon.used_count} < Success count {success_count}")
