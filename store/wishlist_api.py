"""
Wishlist API Views for VIBE E-Commerce
REST API endpoints for wishlist operations.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
@require_http_methods(["GET"])
def wishlist_list(_request):
    """Get user's wishlist."""
    # pylint: disable=import-outside-toplevel
    from store.wishlist_service import WishlistService
    service = WishlistService(_request.user)
    wishlist = service.get_wishlist()
    return JsonResponse({
        'success': True,
        'count': len(wishlist),
        'items': wishlist,
    })


@login_required
@require_http_methods(["POST"])
def wishlist_add(request, product_id):
    """Add product to wishlist."""
    # pylint: disable=import-outside-toplevel
    from store.wishlist_service import WishlistService
    service = WishlistService(request.user)
    result = service.add_to_wishlist(product_id)
    return JsonResponse(result)


@login_required
@require_http_methods(["DELETE"])
def wishlist_remove(request, product_id):
    """Remove product from wishlist."""
    # pylint: disable=import-outside-toplevel
    from store.wishlist_service import WishlistService
    service = WishlistService(request.user)
    result = service.remove_from_wishlist(product_id)
    return JsonResponse(result)


@login_required
@require_http_methods(["GET"])
def wishlist_check(request, product_id):
    """Check if product is in wishlist."""
    # pylint: disable=import-outside-toplevel
    from store.wishlist_service import WishlistService
    service = WishlistService(request.user)
    in_wishlist = service.is_in_wishlist(product_id)
    return JsonResponse({
        'success': True,
        'in_wishlist': in_wishlist,
    })


@login_required
@require_http_methods(["GET"])
def wishlist_price_drops(request):
    """Get wishlist items with price drops."""
    # pylint: disable=import-outside-toplevel
    from store.wishlist_service import WishlistService
    service = WishlistService(request.user)
    price_drops = service.get_price_drops()
    return JsonResponse({
        'success': True,
        'count': len(price_drops),
        'items': price_drops,
    })


@login_required
@require_http_methods(["POST"])
def wishlist_move_to_cart(request, product_id):
    """Move wishlist item to cart."""
    # pylint: disable=import-outside-toplevel
    import json
    from store.wishlist_service import WishlistService
    service = WishlistService(request.user)

    quantity = 1
    if request.body:
        try:
            data = json.loads(request.body)
            quantity = data.get('quantity', 1)
        except json.JSONDecodeError:
            pass

    result = service.move_to_cart(product_id, quantity)
    return JsonResponse(result)


@login_required
@require_http_methods(["DELETE"])
def wishlist_clear(request):
    """Clear all items from wishlist."""
    # pylint: disable=import-outside-toplevel
    from store.wishlist_service import WishlistService
    service = WishlistService(request.user)
    result = service.clear_wishlist()
    return JsonResponse(result)


@login_required
@require_http_methods(["GET"])
def wishlist_count(request):
    """Get wishlist item count."""
    # pylint: disable=import-outside-toplevel
    from store.wishlist_service import WishlistService
    service = WishlistService(request.user)
    count = service.get_wishlist_count()
    return JsonResponse({
        'success': True,
        'count': count,
    })
