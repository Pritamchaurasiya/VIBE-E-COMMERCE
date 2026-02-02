import threading
import concurrent.futures
from decimal import Decimal
from django.test import TransactionTestCase
from django.db import connection
from store.models import Coupon
from store.coupon_service import CouponService
from django.utils import timezone
from datetime import timedelta

class CouponConcurrencyTest(TransactionTestCase):
    """Test coupon concurrency issues."""

    def setUp(self):
        self.code = "RACE_TEST"
        self.coupon = Coupon.objects.create(
            code=self.code,
            discount_type='fixed',
            discount_value=10,
            min_order_value=0,
            max_uses=10,
            used_count=0,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            is_active=True
        )
        self.service = CouponService()

    def test_concurrent_coupon_application(self):
        """Test applying coupon concurrently respects max_uses."""
        # This test attempts to apply the coupon more times than allowed concurrently
        num_threads = 20
        # Only 10 should succeed because max_uses=10

        def apply_task():
            # Create a new connection for each thread to simulate concurrent requests
            connection.close()
            success, _ = self.service.apply_coupon(self.code)
            return success

        successful_applications = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(apply_task) for _ in range(num_threads)]
            for future in concurrent.futures.as_completed(futures):
                try:
                    if future.result():
                        successful_applications += 1
                except Exception:
                    pass

        self.coupon.refresh_from_db()

        # In SQLite, we might get fewer successes due to 'database is locked' errors,
        # but we must NEVER get more successes than max_uses.
        self.assertLessEqual(successful_applications, self.coupon.max_uses)
        self.assertEqual(self.coupon.used_count, successful_applications)
