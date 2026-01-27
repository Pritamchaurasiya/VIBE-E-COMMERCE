import pytest
from django.utils import timezone
from store.models import Coupon
from store.coupon_service import CouponService

@pytest.mark.django_db
def test_coupon_apply_enforces_limit():
    """
    Test that apply_coupon enforces max_uses limit at the database level.
    """
    # Create a coupon with max_uses=1
    coupon = Coupon.objects.create(
        code="TESTLIMIT",
        discount_type="fixed",
        discount_value=10,
        max_uses=1,
        used_count=0,
        valid_from=timezone.now() - timezone.timedelta(days=1),
        valid_until=timezone.now() + timezone.timedelta(days=1),
        is_active=True
    )

    service = CouponService()

    # First application should succeed
    success, msg = service.apply_coupon("TESTLIMIT")
    assert success is True, f"First application failed: {msg}"

    # Reload from DB to verify increment
    coupon.refresh_from_db()
    assert coupon.used_count == 1

    # Second application should fail
    success, msg = service.apply_coupon("TESTLIMIT")

    # In the vulnerable version, this might succeed (return True) or fail depending on logic,
    # but the critical part is whether the DB was updated.
    # The current code blindly increments.

    coupon.refresh_from_db()
    assert coupon.used_count == 1, f"Security Vulnerability: Coupon usage limit bypassed! used_count is {coupon.used_count}"
    assert success is False, "Second application should report failure"
