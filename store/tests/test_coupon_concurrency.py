from django.test import TransactionTestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService
import concurrent.futures
from decimal import Decimal

class CouponConcurrencyTest(TransactionTestCase):
    def setUp(self):
        # Create a coupon with max_uses=1
        self.coupon_code = "RACE100"
        self.coupon = Coupon.objects.create(
            code=self.coupon_code,
            discount_type='fixed',
            discount_value=Decimal("10.00"),
            min_order_value=Decimal("0.00"),
            max_uses=1,
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )
        self.service = CouponService()

    def test_coupon_race_condition(self):
        """
        Test that concurrent applications of a coupon with max_uses=1
        do not result in used_count > max_uses.
        """
        def apply_coupon_worker():
            # Each worker tries to apply the coupon
            # In a real scenario, this would be triggered by a request
            success, message = self.service.apply_coupon(self.coupon_code)
            return success

        # Simulate 5 concurrent users trying to apply the coupon
        num_threads = 5
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(apply_coupon_worker) for _ in range(num_threads)]
            results = [f.result() for f in futures]

        # Refresh from DB
        self.coupon.refresh_from_db()

        print(f"Used count: {self.coupon.used_count}")
        print(f"Results: {results}")

        # Assert that only 1 succeeded
        success_count = results.count(True)
        self.assertEqual(self.coupon.used_count, 1, f"Coupon used_count should be 1, got {self.coupon.used_count}")
        self.assertEqual(success_count, 1, f"Only 1 application should succeed, got {success_count}")
