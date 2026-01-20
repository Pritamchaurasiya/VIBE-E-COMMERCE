"""
Coupon Service for VIBE E-Commerce.

Provides coupon validation, discount calculation, and auto-apply functionality.
"""
import logging
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger(__name__)


@dataclass
class CouponResult:
    """Result of coupon validation."""
    valid: bool
    discount_amount: Decimal
    error_message: str = ""
    coupon_code: str = ""
    discount_type: str = ""
    discount_value: Decimal = Decimal("0")


class CouponService:
    """
    Service for coupon validation and discount calculations.
    """

    def __init__(self, user=None):
        """Initialize with optional user."""
        self.user = user

    def _get_coupon_model(self):
        """Lazy import to avoid circular imports."""
        # pylint: disable=import-outside-toplevel
        from store.models import Coupon
        return Coupon

    def validate_coupon(
        self,
        code: str,
        cart_total: Decimal,
        cart_items: Optional[List] = None
    ) -> CouponResult:
        """
        Validate a coupon code against cart.

        Args:
            code: Coupon code to validate
            cart_total: Total cart value
            cart_items: Optional list of cart items

        Returns:
            CouponResult with validation status and discount
        """
        if not code:
            return CouponResult(
                valid=False,
                discount_amount=Decimal("0"),
                error_message="Please enter a coupon code"
            )

        Coupon = self._get_coupon_model()

        try:
            # pylint: disable=no-member
            coupon = Coupon.objects.get(code__iexact=code.strip())
        except Coupon.DoesNotExist:
            return CouponResult(
                valid=False,
                discount_amount=Decimal("0"),
                error_message="Invalid coupon code"
            )

        # Check if coupon is active
        if not coupon.is_active:
            return CouponResult(
                valid=False,
                discount_amount=Decimal("0"),
                error_message="This coupon is no longer active"
            )

        # Check validity dates
        now = timezone.now()
        if now < coupon.valid_from:
            return CouponResult(
                valid=False,
                discount_amount=Decimal("0"),
                error_message="This coupon is not yet valid"
            )

        if now > coupon.valid_until:
            return CouponResult(
                valid=False,
                discount_amount=Decimal("0"),
                error_message="This coupon has expired"
            )

        # Check usage limit
        if coupon.used_count >= coupon.max_uses:
            return CouponResult(
                valid=False,
                discount_amount=Decimal("0"),
                error_message="This coupon has reached its usage limit"
            )

        # Check minimum order value
        if cart_total < coupon.min_order_value:
            return CouponResult(
                valid=False,
                discount_amount=Decimal("0"),
                error_message=f"Minimum order value is ₹{coupon.min_order_value}"
            )

        # Calculate discount
        discount_amount = self._calculate_discount(
            coupon.discount_type,
            coupon.discount_value,
            cart_total
        )

        return CouponResult(
            valid=True,
            discount_amount=discount_amount,
            coupon_code=coupon.code,
            discount_type=coupon.discount_type,
            discount_value=coupon.discount_value
        )

    def _calculate_discount(
        self,
        discount_type: str,
        discount_value: Decimal,
        cart_total: Decimal
    ) -> Decimal:
        """Calculate discount amount based on type."""
        if discount_type == 'percent':
            discount = cart_total * (discount_value / Decimal("100"))
            # Cap at reasonable maximum (e.g., 50% of cart)
            max_discount = cart_total * Decimal("0.5")
            return min(discount, max_discount)
        elif discount_type == 'fixed':
            # Don't allow discount more than cart total
            return min(discount_value, cart_total)
        else:
            return Decimal("0")

    def get_best_coupon(
        self,
        cart_total: Decimal,
        cart_items: Optional[List] = None
    ) -> Optional[CouponResult]:
        """
        Find the best applicable coupon for the cart.

        Args:
            cart_total: Total cart value
            cart_items: Optional list of cart items

        Returns:
            Best CouponResult or None if no valid coupons
        """
        Coupon = self._get_coupon_model()
        now = timezone.now()

        # Get all valid coupons
        # pylint: disable=no-member
        valid_coupons = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now,
            min_order_value__lte=cart_total,
        ).exclude(
            used_count__gte=Q(max_uses=0) | Q(max_uses__gt=0, used_count__gte='max_uses')
        )

        best_result = None
        best_discount = Decimal("0")

        for coupon in valid_coupons:
            if coupon.used_count < coupon.max_uses:
                result = self.validate_coupon(coupon.code, cart_total, cart_items)
                if result.valid and result.discount_amount > best_discount:
                    best_discount = result.discount_amount
                    best_result = result

        return best_result

    def get_available_coupons(self, cart_total: Decimal = Decimal("0")) -> List[Dict]:
        """
        Get all available coupons for display.

        Args:
            cart_total: Optional cart total to check eligibility

        Returns:
            List of coupon dictionaries
        """
        Coupon = self._get_coupon_model()
        now = timezone.now()

        # pylint: disable=no-member
        coupons = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now,
        ).order_by('-discount_value')

        coupon_list = []
        for coupon in coupons:
            if coupon.used_count < coupon.max_uses:
                is_eligible = cart_total >= coupon.min_order_value if cart_total else False

                coupon_list.append({
                    'code': coupon.code,
                    'discount_type': coupon.discount_type,
                    'discount_value': str(coupon.discount_value),
                    'min_order_value': str(coupon.min_order_value),
                    'valid_until': coupon.valid_until.isoformat(),
                    'is_eligible': is_eligible,
                    'description': self._get_coupon_description(coupon),
                    'savings_text': self._get_savings_text(coupon, cart_total),
                })

        return coupon_list

    def _get_coupon_description(self, coupon) -> str:
        """Generate human-readable coupon description."""
        if coupon.discount_type == 'percent':
            desc = f"Get {coupon.discount_value}% off"
        else:
            desc = f"Get ₹{coupon.discount_value} off"

        if coupon.min_order_value > 0:
            desc += f" on orders above ₹{coupon.min_order_value}"

        return desc

    def _get_savings_text(self, coupon, cart_total: Decimal) -> str:
        """Generate savings text for coupon."""
        if cart_total <= 0:
            return ""

        if cart_total < coupon.min_order_value:
            needed = coupon.min_order_value - cart_total
            return f"Add ₹{needed:.0f} more to use"

        discount = self._calculate_discount(
            coupon.discount_type,
            coupon.discount_value,
            cart_total
        )
        return f"You save ₹{discount:.0f}"

    def apply_coupon(self, code: str) -> Tuple[bool, str]:
        """
        Apply a coupon (increment usage count).

        Args:
            code: Coupon code to apply

        Returns:
            Tuple of (success, message)
        """
        Coupon = self._get_coupon_model()
        from django.db.models import F

        try:
            # pylint: disable=no-member
            # Use atomic update with condition to prevent race condition
            rows_updated = Coupon.objects.filter(
                code__iexact=code.strip(),
                used_count__lt=F('max_uses')
            ).update(used_count=F('used_count') + 1)

            if rows_updated == 1:
                logger.info("Coupon %s applied successfully", code)
                return True, "Coupon applied successfully"

            # If no rows updated, check why
            if not Coupon.objects.filter(code__iexact=code.strip()).exists():
                return False, "Coupon not found"

            return False, "Coupon usage limit reached"

        except Exception as exc:
            logger.error("Error applying coupon: %s", exc)
            return False, "Error applying coupon"
