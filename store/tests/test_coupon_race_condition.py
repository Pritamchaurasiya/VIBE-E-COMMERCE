import threading
from django.test import TransactionTestCase
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService

class CouponRaceConditionTest(TransactionTestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code="RACE10",
            discount_type="percent",
            discount_value=10,
            max_uses=5,
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )
        self.service = CouponService()

    def test_concurrent_coupon_application(self):
        """Test concurrent applications of a coupon."""

        results = []

        def apply_coupon():
            success, msg = self.service.apply_coupon("RACE10")
            results.append(success)

        threads = []
        # Try to apply 20 times, limit is 5
        for _ in range(20):
            t = threading.Thread(target=apply_coupon)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        success_count = results.count(True)
        self.coupon.refresh_from_db()

        print(f"Success count: {success_count}")
        print(f"Final used_count: {self.coupon.used_count}")

        # In a race condition, we expect more than 5 successes
        # OR used_count < success_count (lost updates)
        # But specifically we want to prevent over-usage

        self.assertLessEqual(success_count, 5, f"Coupon used {success_count} times, limit was 5")
        self.assertEqual(self.coupon.used_count, success_count, "Used count does not match success count")
