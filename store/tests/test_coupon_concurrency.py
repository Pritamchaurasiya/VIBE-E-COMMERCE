from django.test import TransactionTestCase
from store.models import Coupon
from store.coupon_service import CouponService
from django.utils import timezone
from datetime import timedelta
import threading
from decimal import Decimal

class CouponConcurrencyTest(TransactionTestCase):
    def setUp(self):
        self.coupon_code = 'RACE10'
        self.coupon = Coupon.objects.create(
            code=self.coupon_code,
            discount_type='percent',
            discount_value=Decimal('10.00'),
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            max_uses=1,
            used_count=0,
            is_active=True
        )
        self.service = CouponService()

    def test_concurrent_coupon_application(self):
        """
        Test that multiple concurrent requests cannot exceed max_uses.
        """
        num_threads = 5
        threads = []
        results = []

        def apply_coupon_worker():
            # Create a new service instance per thread to simulate separate requests
            service = CouponService()
            success, message = service.apply_coupon(self.coupon_code)
            results.append(success)

        for _ in range(num_threads):
            t = threading.Thread(target=apply_coupon_worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Refresh coupon from DB
        self.coupon.refresh_from_db()

        print(f"Coupon used count: {self.coupon.used_count}")
        print(f"Success results: {results}")

        # In a race condition, used_count might be > 1
        # and successful applications might be > 1
        self.assertLessEqual(self.coupon.used_count, 1, f"Coupon used {self.coupon.used_count} times, expected max 1")
        self.assertEqual(results.count(True), 1, f"Coupon applied successfully {results.count(True)} times, expected max 1")
