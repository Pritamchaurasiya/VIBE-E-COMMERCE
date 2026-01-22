
import threading
from concurrent.futures import ThreadPoolExecutor
from django.test import TransactionTestCase
from django.utils import timezone
from datetime import timedelta
from store.models import Coupon
from store.coupon_service import CouponService

class CouponRaceConditionTest(TransactionTestCase):
    """Test suite for coupon race conditions."""

    def test_coupon_concurrency(self):
        """Test that coupon usage limits are respected under concurrent load."""
        code = "RACE_TEST_100"

        # Create coupon with limit of 10
        coupon = Coupon.objects.create(
            code=code,
            discount_type='fixed',
            discount_value=10,
            min_order_value=0,
            max_uses=10,
            used_count=0,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            is_active=True
        )

        service = CouponService()
        success_count = 0
        lock = threading.Lock()

        def apply():
            nonlocal success_count
            # Apply coupon - this simulates checking out
            success, _ = service.apply_coupon(code)
            if success:
                with lock:
                    success_count += 1

        # Simulate 20 concurrent requests (more than the limit of 10)
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(apply) for _ in range(20)]
            for f in futures:
                f.result()

        # Reload from DB
        coupon.refresh_from_db()

        # Verify
        self.assertEqual(coupon.used_count, 10, "Used count should be exactly 10")
        self.assertEqual(success_count, 10, "Should only have 10 successful applications")
        self.assertEqual(coupon.used_count, success_count, "DB count and success count should match")
