"""
Search API Views for VIBE E-Commerce
REST API endpoints for search operations.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@require_http_methods(["GET"])
def search_products(request):
    """Search for products."""
    # pylint: disable=import-outside-toplevel
    from store.search_service import SearchService

    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort', 'relevance')
    in_stock_only = request.GET.get('in_stock', '').lower() == 'true'
    limit = min(int(request.GET.get('limit', 50)), 100)
    offset = int(request.GET.get('offset', 0))

    user = request.user if request.user.is_authenticated else None
    service = SearchService(user)

    results = service.search_products(
        query=query,
        category_id=int(category_id) if category_id else None,
        min_price=float(min_price) if min_price else None,
        max_price=float(max_price) if max_price else None,
        sort_by=sort_by,
        in_stock_only=in_stock_only,
        limit=limit,
        offset=offset,
    )

    return JsonResponse({
        'success': True,
        **results,
    })


@require_http_methods(["GET"])
def search_autocomplete(request):
    """Get autocomplete suggestions."""
    # pylint: disable=import-outside-toplevel
    from store.search_service import SearchService

    query = request.GET.get('q', '')
    user = request.user if request.user.is_authenticated else None
    service = SearchService(user)

    suggestions = service.get_autocomplete(query)
    return JsonResponse({
        'success': True,
        'suggestions': suggestions,
    })


@require_http_methods(["GET"])
def search_filters(request):
    """Get available search filters."""
    # pylint: disable=import-outside-toplevel
    from store.search_service import SearchService

    query = request.GET.get('q', '')
    service = SearchService()

    filters = service.get_search_filters(query)
    return JsonResponse({
        'success': True,
        **filters,
    })


@require_http_methods(["GET"])
def search_popular(_request):
    """Get popular searches."""
    # pylint: disable=import-outside-toplevel
    from store.search_service import SearchService

    service = SearchService()
    popular = service.get_popular_searches()

    return JsonResponse({
        'success': True,
        'searches': popular,
    })


@login_required
@require_http_methods(["GET"])
def search_recent(request):
    """Get user's recent searches."""
    # pylint: disable=import-outside-toplevel
    from store.search_service import SearchService

    service = SearchService(request.user)
    recent = service.get_recent_searches()

    return JsonResponse({
        'success': True,
        'searches': recent,
    })


@login_required
@require_http_methods(["DELETE"])
def search_clear_recent(request):
    """Clear user's recent searches."""
    # pylint: disable=import-outside-toplevel
    from store.search_service import SearchService

    service = SearchService(request.user)
    service.clear_recent_searches()

    return JsonResponse({
        'success': True,
        'message': 'Recent searches cleared',
    })
