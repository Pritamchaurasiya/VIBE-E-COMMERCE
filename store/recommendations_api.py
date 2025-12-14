"""
Recommendation API Views
REST API endpoints for product recommendations and search suggestions.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .recommendations import RecommendationEngine, SearchSuggestionEngine


@api_view(['GET'])
@permission_classes([AllowAny])
def similar_products(request, product_id):
    """
    Get products similar to the specified product.

    Query Parameters:
        - limit: Number of products to return (default: 8, max: 20)
    """
    limit = min(int(request.GET.get('limit', 8)), 20)

    engine = RecommendationEngine(user=request.user)
    products = engine.get_similar_products(product_id, limit=limit)

    return Response({
        'status': 'success',
        'count': len(products),
        'products': products,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def frequently_bought_together(request, product_id):
    """
    Get products frequently bought together with the specified product.

    Query Parameters:
        - limit: Number of products to return (default: 4, max: 10)
    """
    limit = min(int(request.GET.get('limit', 4)), 10)

    engine = RecommendationEngine(user=request.user)
    products = engine.get_frequently_bought_together(product_id, limit=limit)

    return Response({
        'status': 'success',
        'count': len(products),
        'products': products,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def personalized_recommendations(request):
    """
    Get personalized product recommendations for the current user.
    Falls back to trending products for anonymous users.

    Query Parameters:
        - limit: Number of products to return (default: 12, max: 24)
    """
    limit = min(int(request.GET.get('limit', 12)), 24)

    engine = RecommendationEngine(user=request.user)
    products = engine.get_personalized_recommendations(limit=limit)

    return Response({
        'status': 'success',
        'personalized': request.user.is_authenticated,
        'count': len(products),
        'products': products,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def trending_products(request):
    """
    Get trending products based on recent orders.

    Query Parameters:
        - limit: Number of products to return (default: 12, max: 24)
    """
    limit = min(int(request.GET.get('limit', 12)), 24)

    engine = RecommendationEngine(user=request.user)
    products = engine.get_trending_products(limit=limit)

    return Response({
        'status': 'success',
        'count': len(products),
        'products': products,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def price_drop_alerts(request):
    """
    Get products in the user's wishlist that have price drops.
    Requires authentication.
    """
    engine = RecommendationEngine(user=request.user)
    alerts = engine.get_price_drop_alerts()

    return Response({
        'status': 'success',
        'count': len(alerts),
        'alerts': alerts,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def restock_suggestions(request):
    """
    Get product restock suggestions based on purchase history.
    Requires authentication.
    """
    engine = RecommendationEngine(user=request.user)
    suggestions = engine.get_restock_suggestions()

    return Response({
        'status': 'success',
        'count': len(suggestions),
        'suggestions': suggestions,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def search_suggestions(request):
    """
    Get search autocomplete suggestions.

    Query Parameters:
        - q: Search query (required, min 2 characters)
        - limit: Number of suggestions per category (default: 10)
    """
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return Response({
            'status': 'error',
            'message': 'Query must be at least 2 characters',
        }, status=status.HTTP_400_BAD_REQUEST)

    limit = min(int(request.GET.get('limit', 10)), 20)

    engine = SearchSuggestionEngine()
    suggestions = engine.get_suggestions(query, limit=limit)

    return Response({
        'status': 'success',
        'query': query,
        'suggestions': suggestions,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def popular_searches(request):
    """
    Get popular search terms.

    Query Parameters:
        - limit: Number of terms to return (default: 10)
    """
    limit = min(int(request.GET.get('limit', 10)), 20)

    engine = SearchSuggestionEngine()
    searches = engine.get_popular_searches(limit=limit)

    return Response({
        'status': 'success',
        'count': len(searches),
        'searches': searches,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def recommendation_dashboard(request):
    """
    Get comprehensive recommendation data for the home page.
    Returns trending, personalized, and category-based recommendations.
    """
    engine = RecommendationEngine(user=request.user)

    data = {
        'trending': engine.get_trending_products(limit=8),
        'personalized': engine.get_personalized_recommendations(limit=8),
    }

    if request.user.is_authenticated:
        data['price_drops'] = engine.get_price_drop_alerts()[:4]
        data['restock'] = engine.get_restock_suggestions()[:4]
    else:
        data['price_drops'] = []
        data['restock'] = []

    return Response({
        'status': 'success',
        'is_authenticated': request.user.is_authenticated,
        'data': data,
    })
