
import threading
import time
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
            discount_type='percent',
            discount_value=Decimal('10.00'),
            max_uses=100, # Large enough to not hit limit
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1)
        )
        self.service = CouponService()

    def test_race_condition(self):
        # We want to simulate concurrent usage
        # 10 threads trying to use a coupon

        success_count = 0
        lock = threading.Lock()

        def apply_coupon():
            nonlocal success_count
            # Ensure each thread has its own connection if needed
            for conn in connections.all():
                conn.close()

            try:
                success, msg = self.service.apply_coupon('RACE10')
                if success:
                    with lock:
                        success_count += 1
            except Exception as e:
                # With SQLite, we expect some "database is locked" errors
                print(f"Thread error: {e}")
            finally:
                for conn in connections.all():
                    conn.close()

        threads = []
        for _ in range(10):
            t = threading.Thread(target=apply_coupon)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.coupon.refresh_from_db()
        print(f"Used count in DB: {self.coupon.used_count}")
        print(f"Successful threads: {success_count}")

        self.assertEqual(self.coupon.used_count, success_count,
                         f"Race condition detected! DB count {self.coupon.used_count} != Success count {success_count}")
