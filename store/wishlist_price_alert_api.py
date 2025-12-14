"""
Wishlist Price Alert API Views for VIBE E-Commerce.

REST API endpoints for wishlist price alerts and notifications.
"""
import json
from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
@require_http_methods(["POST"])
def set_price_alert(request, product_id):
    """
    Set a price alert for a wishlist item.

    POST /api/v1/wishlist/<product_id>/price-alert/
    Body: {"target_price": 500, "notify_on_sale": true, "notify_on_restock": false}
    """
    # pylint: disable=import-outside-toplevel
    from store.models import Wishlist

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON',
        }, status=400)

    try:
        # pylint: disable=no-member
        wishlist_item = Wishlist.objects.get(
            user=request.user,
            product_id=product_id
        )
    except Wishlist.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Product not in wishlist',
        }, status=404)

    # Update price alert settings
    if 'target_price' in data and data['target_price']:
        wishlist_item.target_price = Decimal(str(data['target_price']))

    if 'notify_on_sale' in data:
        wishlist_item.notify_on_sale = bool(data['notify_on_sale'])

    if 'notify_on_restock' in data:
        wishlist_item.notify_on_restock = bool(data['notify_on_restock'])

    wishlist_item.save()

    return JsonResponse({
        'success': True,
        'message': 'Price alert settings updated',
        'settings': {
            'target_price': str(wishlist_item.target_price) if wishlist_item.target_price else None,
            'notify_on_sale': wishlist_item.notify_on_sale,
            'notify_on_restock': wishlist_item.notify_on_restock,
        },
    })


@login_required
@require_http_methods(["DELETE"])
def remove_price_alert(request, product_id):
    """
    Remove price alert from a wishlist item.

    DELETE /api/v1/wishlist/<product_id>/price-alert/
    """
    # pylint: disable=import-outside-toplevel
    from store.models import Wishlist

    try:
        # pylint: disable=no-member
        wishlist_item = Wishlist.objects.get(
            user=request.user,
            product_id=product_id
        )
    except Wishlist.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Product not in wishlist',
        }, status=404)

    wishlist_item.target_price = None
    wishlist_item.notify_on_sale = False
    wishlist_item.notify_on_restock = False
    wishlist_item.save()

    return JsonResponse({
        'success': True,
        'message': 'Price alert removed',
    })


@login_required
@require_http_methods(["GET"])
def get_price_alerts(request):
    """
    Get all wishlist items with price alerts.

    GET /api/v1/wishlist/price-alerts/
    """
    # pylint: disable=import-outside-toplevel
    from store.models import Wishlist
    from django.db.models import Q

    # pylint: disable=no-member
    items = Wishlist.objects.filter(
        user=request.user
    ).filter(
        Q(target_price__isnull=False) |
        Q(notify_on_sale=True) |
        Q(notify_on_restock=True)
    ).select_related('product', 'product__category')

    alerts = []
    for item in items:
        product = item.product

        # Check alert status
        alert_status = 'watching'
        if item.target_price_reached:
            alert_status = 'target_reached'
        elif item.has_price_drop:
            alert_status = 'price_dropped'
        elif not product.is_in_stock and item.notify_on_restock:
            alert_status = 'out_of_stock'

        alerts.append({
            'product_id': product.id,
            'product_name': product.name,
            'product_slug': product.slug,
            'product_image': product.image.url if product.image else None,
            'current_price': str(product.price),
            'price_when_added': str(item.price_when_added) if item.price_when_added else None,
            'target_price': str(item.target_price) if item.target_price else None,
            'notify_on_sale': item.notify_on_sale,
            'notify_on_restock': item.notify_on_restock,
            'in_stock': product.is_in_stock,
            'alert_status': alert_status,
            'price_drop': {
                'amount': str(item.price_drop_amount),
                'percentage': round(float(item.price_drop_percentage), 1),
            } if item.has_price_drop else None,
        })

    return JsonResponse({
        'success': True,
        'count': len(alerts),
        'alerts': alerts,
    })


@login_required
@require_http_methods(["GET"])
def check_price_alerts(request):
    """
    Check for triggered price alerts (items where target reached).

    GET /api/v1/wishlist/price-alerts/check/
    """
    # pylint: disable=import-outside-toplevel
    from store.models import Wishlist
    from django.db.models import F

    # pylint: disable=no-member
    triggered = Wishlist.objects.filter(
        user=request.user,
        target_price__isnull=False,
        product__price__lte=F('target_price')
    ).select_related('product')

    items = []
    for item in triggered:
        product = item.product
        savings = item.target_price - product.price if item.target_price else 0

        items.append({
            'product_id': product.id,
            'product_name': product.name,
            'product_slug': product.slug,
            'current_price': str(product.price),
            'target_price': str(item.target_price),
            'savings': str(savings),
        })

    return JsonResponse({
        'success': True,
        'triggered_count': len(items),
        'items': items,
    })
