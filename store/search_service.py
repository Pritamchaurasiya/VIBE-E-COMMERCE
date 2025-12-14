"""
Search Service for VIBE E-Commerce
Provides advanced search functionality with autocomplete, filters, and analytics.
"""
import logging
from typing import Dict, List, Optional

from django.db.models import Q, Count, Min, Max
from django.core.cache import cache
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class SearchService:
    """
    Service for product and content search.
    """

    CACHE_TIMEOUT = 600  # 10 minutes
    MAX_SUGGESTIONS = 10
    MAX_RECENT_SEARCHES = 5

    def __init__(self, user: Optional[User] = None):
        self.user = user

    def _get_model(self, model_name: str):
        """Lazy import to avoid circular imports."""
        # pylint: disable=import-outside-toplevel
        from store.models import Product, Category, Vendor
        models_map = {
            'Product': Product,
            'Category': Category,
            'Vendor': Vendor,
        }
        return models_map.get(model_name)

    def search_products(
        self,
        query: str,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = 'relevance',
        in_stock_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict:
        """
        Search for products.

        Args:
            query: Search query
            category_id: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            sort_by: Sort order (relevance, price_low, price_high, newest, rating)
            in_stock_only: Only show in-stock products
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Search results with products and metadata
        """
        # pylint: disable=invalid-name
        product_model = self._get_model('Product')

        # pylint: disable=no-member
        queryset = product_model.objects.filter(is_active=True)

        # Text search
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(vendor__name__icontains=query)
            )

            # Track search query
            self._track_search(query)

        # Apply filters
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)

        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

        if in_stock_only:
            queryset = queryset.filter(stock__gt=0)

        # Get total count before pagination
        total_count = queryset.count()

        # Apply sorting
        sort_options = {
            'relevance': '-created_at',  # Default to newest for now
            'price_low': 'price',
            'price_high': '-price',
            'newest': '-created_at',
            'rating': '-average_rating',
            'popular': '-view_count',
        }
        order_field = sort_options.get(sort_by, '-created_at')
        queryset = queryset.order_by(order_field)

        # Pagination
        products = queryset.select_related(
            'category', 'vendor'
        )[offset:offset + limit]

        # Format results
        results = [
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'price': str(p.price),
                'original_price': str(p.original_price) if hasattr(p, 'original_price') and p.original_price else None,
                'image': p.image.url if p.image else None,
                'category': {
                    'id': p.category.id,
                    'name': p.category.name,
                } if p.category else None,
                'vendor': {
                    'id': p.vendor.id,
                    'name': p.vendor.name,
                } if p.vendor else None,
                'in_stock': p.stock > 0 if hasattr(p, 'stock') else True,
                'rating': getattr(p, 'average_rating', None),
            }
            for p in products
        ]

        return {
            'query': query,
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'products': results,
        }

    def get_autocomplete(self, query: str) -> List[Dict]:
        """
        Get autocomplete suggestions.

        Args:
            query: Partial search query

        Returns:
            List of suggestions
        """
        if not query or len(query) < 2:
            return []

        cache_key = f'autocomplete_{query.lower()}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        suggestions = []

        # pylint: disable=invalid-name
        product_model = self._get_model('Product')
        category_model = self._get_model('Category')

        # Product name suggestions
        # pylint: disable=no-member
        products = product_model.objects.filter(
            is_active=True,
            name__icontains=query
        ).values('name')[:5]

        for p in products:
            suggestions.append({
                'type': 'product',
                'text': p['name'],
                'icon': '📦',
            })

        # Category suggestions
        # pylint: disable=no-member
        categories = category_model.objects.filter(
            name__icontains=query
        ).values('name', 'id')[:3]

        for c in categories:
            suggestions.append({
                'type': 'category',
                'text': c['name'],
                'id': c['id'],
                'icon': '📁',
            })

        # Popular search suggestions
        popular = self.get_popular_searches()
        for search in popular[:2]:
            if query.lower() in search['query'].lower():
                suggestions.append({
                    'type': 'popular',
                    'text': search['query'],
                    'count': search['count'],
                    'icon': '🔥',
                })

        # Limit and cache
        suggestions = suggestions[:self.MAX_SUGGESTIONS]
        cache.set(cache_key, suggestions, self.CACHE_TIMEOUT)

        return suggestions

    def get_popular_searches(self) -> List[Dict]:
        """Get popular search terms."""
        cache_key = 'popular_searches'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # In production, this would query a search analytics table
        # For now, return static popular searches
        popular = [
            {'query': 'organic fertilizer', 'count': 1523},
            {'query': 'seeds', 'count': 1289},
            {'query': 'pesticide', 'count': 1156},
            {'query': 'irrigation', 'count': 987},
            {'query': 'tractor parts', 'count': 876},
        ]

        cache.set(cache_key, popular, self.CACHE_TIMEOUT * 6)
        return popular

    def get_recent_searches(self) -> List[str]:
        """Get user's recent searches."""
        if not self.user:
            return []

        cache_key = f'recent_searches_{self.user.id}'
        return cache.get(cache_key, [])

    def _track_search(self, query: str):
        """Track a search query."""
        if not self.user:
            return

        cache_key = f'recent_searches_{self.user.id}'
        recent = cache.get(cache_key, [])

        # Add to front, remove duplicates
        if query in recent:
            recent.remove(query)
        recent.insert(0, query)

        # Keep only recent searches
        recent = recent[:self.MAX_RECENT_SEARCHES]
        cache.set(cache_key, recent, 86400)  # 24 hours

    def get_search_filters(self, query: str = '') -> Dict:
        """
        Get available filters for search results.

        Args:
            query: Search query to base filters on

        Returns:
            Available filter options
        """
        # pylint: disable=invalid-name
        product_model = self._get_model('Product')
        category_model = self._get_model('Category')

        # pylint: disable=no-member
        base_query = product_model.objects.filter(is_active=True)
        if query:
            base_query = base_query.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )

        # Category filter counts
        # pylint: disable=no-member
        categories = category_model.objects.annotate(
            product_count=Count('product', filter=Q(product__is_active=True))
        ).filter(product_count__gt=0).values('id', 'name', 'product_count')[:20]

        # Price range
        price_stats = base_query.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
        ) if base_query.exists() else {'min_price': 0, 'max_price': 10000}

        return {
            'categories': list(categories),
            'price_range': {
                'min': float(price_stats.get('min_price') or 0),
                'max': float(price_stats.get('max_price') or 10000),
            },
            'sort_options': [
                {'value': 'relevance', 'label': 'Relevance'},
                {'value': 'price_low', 'label': 'Price: Low to High'},
                {'value': 'price_high', 'label': 'Price: High to Low'},
                {'value': 'newest', 'label': 'Newest First'},
                {'value': 'rating', 'label': 'Highest Rated'},
            ],
        }

    def clear_recent_searches(self) -> bool:
        """Clear user's recent searches."""
        if not self.user:
            return False

        cache_key = f'recent_searches_{self.user.id}'
        cache.delete(cache_key)
        return True
