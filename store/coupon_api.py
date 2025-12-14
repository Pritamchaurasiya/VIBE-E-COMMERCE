"""
Coupon API Views for VIBE E-Commerce.

REST API endpoints for coupon validation and management.
"""
import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from store.coupon_service import CouponService


@require_http_methods(["POST"])
def validate_coupon(request):
    """
    Validate a coupon code.

    POST /api/v1/coupons/validate/
    Body: {"code": "SAVE20", "cart_total": 1000}
    """
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON',
        }, status=400)

    code = data.get('code', '')
    cart_total = Decimal(str(data.get('cart_total', 0)))

    user = request.user if request.user.is_authenticated else None
    service = CouponService(user)

    result = service.validate_coupon(code, cart_total)

    if result.valid:
        return JsonResponse({
            'success': True,
            'valid': True,
            'coupon_code': result.coupon_code,
            'discount_type': result.discount_type,
            'discount_value': str(result.discount_value),
            'discount_amount': str(result.discount_amount),
            'new_total': str(cart_total - result.discount_amount),
        })
    else:
        return JsonResponse({
            'success': True,
            'valid': False,
            'error': result.error_message,
        })


@require_http_methods(["GET"])
def get_best_coupon(request):
    """
    Get the best coupon for current cart.

    GET /api/v1/coupons/best/?cart_total=1000
    """
    cart_total = Decimal(request.GET.get('cart_total', '0'))

    if cart_total <= 0:
        return JsonResponse({
            'success': False,
            'error': 'Cart total is required',
        }, status=400)

    user = request.user if request.user.is_authenticated else None
    service = CouponService(user)

    result = service.get_best_coupon(cart_total)

    if result:
        return JsonResponse({
            'success': True,
            'found': True,
            'coupon': {
                'code': result.coupon_code,
                'discount_type': result.discount_type,
                'discount_value': str(result.discount_value),
                'discount_amount': str(result.discount_amount),
                'new_total': str(cart_total - result.discount_amount),
            },
        })
    else:
        return JsonResponse({
            'success': True,
            'found': False,
            'message': 'No applicable coupons found',
        })


@require_http_methods(["GET"])
def list_available_coupons(request):
    """
    List all available coupons.

    GET /api/v1/coupons/available/?cart_total=1000
    """
    cart_total = Decimal(request.GET.get('cart_total', '0'))

    user = request.user if request.user.is_authenticated else None
    service = CouponService(user)

    coupons = service.get_available_coupons(cart_total)

    return JsonResponse({
        'success': True,
        'count': len(coupons),
        'coupons': coupons,
    })


@login_required
@require_http_methods(["POST"])
def apply_coupon_to_order(request):
    """
    Apply coupon and increment usage (called after successful order).

    POST /api/v1/coupons/apply/
    Body: {"code": "SAVE20"}
    """
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON',
        }, status=400)

    code = data.get('code', '')

    if not code:
        return JsonResponse({
            'success': False,
            'error': 'Coupon code is required',
        }, status=400)

    service = CouponService(request.user)
    success, message = service.apply_coupon(code)

    return JsonResponse({
        'success': success,
        'message': message,
    })
