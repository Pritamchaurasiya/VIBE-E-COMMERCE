import threading
from decimal import Decimal
from django.test import TransactionTestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService

class CouponConcurrencyTest(TransactionTestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code='TEST100',
            discount_type='fixed',
            discount_value=Decimal('100.00'),
            max_uses=1,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            min_order_value=Decimal('500.00')
        )
        self.service = CouponService()

    def test_concurrent_coupon_usage(self):
        """
        Test that multiple threads trying to use a coupon with max_uses=1
        results in only one successful application.
        """
        num_threads = 5
        results = []

        def apply_coupon_worker():
            # In a real scenario, validation happens first.
            # But here we are testing apply_coupon's resilience.
            # Even if we called validate_coupon first, the race would happen between validation and application.
            # So we simulate requests that have 'passed' validation (or skipped it) and are hitting apply.
            success, message = self.service.apply_coupon('TEST100')
            results.append(success)

        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=apply_coupon_worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        success_count = sum(1 for r in results if r)

        self.coupon.refresh_from_db()

        print(f"\nSuccess count: {success_count}")
        print(f"Coupon used count: {self.coupon.used_count}")

        # Without fix, apply_coupon increments blindly, so success_count will be 5.
        # With fix, it should be 1.
        self.assertEqual(success_count, 1, f"Race condition! {success_count} threads succeeded.")
        self.assertEqual(self.coupon.used_count, 1, "Used count exceeded max uses")
