import pytest
from django.test import TransactionTestCase
from store.models import Coupon
from store.coupon_service import CouponService
from django.utils import timezone
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor

class CouponConcurrencyTest(TransactionTestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code='CONCURRENCY_TEST',
            discount_type='fixed',
            discount_value=10,
            min_order_value=0,
            max_uses=5,
            used_count=0,
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            is_active=True
        )
        self.service = CouponService()

    def test_concurrent_coupon_application(self):
        def apply_coupon():
            # Create a new service instance per thread to simulate requests
            service = CouponService()
            success, _ = service.apply_coupon('CONCURRENCY_TEST')
            return success

        num_threads = 20
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            results = list(executor.map(lambda _: apply_coupon(), range(num_threads)))

        self.coupon.refresh_from_db()

        # Verify strict enforcement
        self.assertLessEqual(self.coupon.used_count, 5, "Used count exceeded max uses")
        self.assertEqual(results.count(True), 5, "Should only allow exactly max_uses successful applications")
