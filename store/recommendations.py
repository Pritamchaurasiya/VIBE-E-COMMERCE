"""
Smart Product Recommendations Service
Provides AI-powered product recommendations based on user behavior,
purchase history, and product similarity.
"""
import logging
from collections import Counter
from datetime import timedelta
from typing import List, Optional

from django.contrib.auth.models import User
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    AI-powered recommendation engine for product suggestions.
    Uses collaborative filtering and content-based approaches.
    """

    CACHE_TIMEOUT = 3600  # 1 hour cache
    MAX_RECOMMENDATIONS = 20

    def __init__(self, user: Optional[User] = None):
        self.user = user

    def _get_model(self, model_name: str):
        """Lazy import to avoid circular imports."""
        # pylint: disable=import-outside-toplevel
        from store.models import (
            Product, Order, OrderItem, Review, Wishlist,
            Category
        )
        models_map = {
            'Product': Product,
            'Order': Order,
            'OrderItem': OrderItem,
            'Review': Review,
            'Wishlist': Wishlist,
            'Category': Category,
        }
        return models_map.get(model_name)

    def _get_recently_viewed_model(self):
        """Lazy import for RecentlyViewed model."""
        # pylint: disable=import-outside-toplevel
        try:
            from store.models import RecentlyViewed
            return RecentlyViewed
        except ImportError:
            return None

    def get_similar_products(
        self,
        product_id: int,
        limit: int = 8
    ) -> List[dict]:
        """
        Get products similar to the given product based on:
        - Same category
        - Same vendor
        - Similar price range
        - Shared tags/attributes
        """
        cache_key = f'similar_products_{product_id}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # pylint: disable=invalid-name
        product_model = self._get_model('Product')

        try:
            # pylint: disable=no-member
            product = product_model.objects.get(id=product_id)
        except product_model.DoesNotExist:
            return []

        # Build similarity query
        price_range_low = float(product.price) * 0.7
        price_range_high = float(product.price) * 1.3

        # pylint: disable=no-member
        similar = product_model.objects.filter(
            is_active=True
        ).exclude(
            id=product_id
        ).filter(
            Q(category=product.category) |
            Q(vendor=product.vendor) |
            Q(price__gte=price_range_low, price__lte=price_range_high)
        ).annotate(
            similarity_score=Count('category')
        ).order_by('-similarity_score', '-created_at')[:limit]

        result = [
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'price': str(p.price),
                'image': p.image.url if p.image else None,
                'category': p.category.name if p.category else None,
                'vendor': p.vendor.name if p.vendor else None,
                'rating': float(p.avg_rating) if p.avg_rating else 0,
            }
            for p in similar
        ]

        cache.set(cache_key, result, self.CACHE_TIMEOUT)
        return result

    def get_frequently_bought_together(
        self,
        product_id: int,
        limit: int = 4
    ) -> List[dict]:
        """
        Get products frequently bought together with the given product.
        Uses order history to find co-purchased items.
        """
        cache_key = f'bought_together_{product_id}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # pylint: disable=invalid-name
        order_item_model = self._get_model('OrderItem')
        product_model = self._get_model('Product')

        # Find orders containing this product
        # pylint: disable=no-member
        order_ids = order_item_model.objects.filter(
            product_id=product_id
        ).values_list('order_id', flat=True)

        # Find other products in those orders
        # pylint: disable=no-member
        co_purchased = order_item_model.objects.filter(
            order_id__in=order_ids
        ).exclude(
            product_id=product_id
        ).values('product_id').annotate(
            co_count=Count('product_id')
        ).order_by('-co_count')[:limit]

        product_ids = [item['product_id'] for item in co_purchased]
        # pylint: disable=no-member
        products = product_model.objects.filter(
            id__in=product_ids,
            is_active=True
        )

        result = [
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'price': str(p.price),
                'image': p.image.url if p.image else None,
            }
            for p in products
        ]

        cache.set(cache_key, result, self.CACHE_TIMEOUT)
        return result

    def get_personalized_recommendations(
        self,
        limit: int = 12
    ) -> List[dict]:
        """
        Get personalized product recommendations for the current user.
        Based on:
        - Purchase history
        - Browsing history
        - Wishlist
        - Category preferences
        """
        if not self.user or not self.user.is_authenticated:
            return self.get_trending_products(limit)

        cache_key = f'personalized_{self.user.id}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # pylint: disable=invalid-name
        product_model = self._get_model('Product')
        order_item_model = self._get_model('OrderItem')
        wishlist_model = self._get_model('Wishlist')
        recently_viewed_model = self._get_recently_viewed_model()

        # Get user's category preferences from purchase history
        # pylint: disable=no-member
        purchased_categories = order_item_model.objects.filter(
            order__user=self.user
        ).values_list('product__category_id', flat=True)

        # Get categories from wishlist
        # pylint: disable=no-member
        wishlist_categories = wishlist_model.objects.filter(
            user=self.user
        ).values_list('product__category_id', flat=True)

        # Get categories from recently viewed (if model exists)
        viewed_categories = []
        if recently_viewed_model:
            # pylint: disable=no-member
            viewed_categories = list(recently_viewed_model.objects.filter(
                user=self.user
            ).values_list('product__category_id', flat=True))

        # Combine and count preferences
        all_categories = (
            list(purchased_categories) +
            list(wishlist_categories) +
            viewed_categories
        )
        category_counts = Counter(all_categories)
        preferred_categories = [
            cat_id for cat_id, _ in category_counts.most_common(5)
        ]

        # Get products user hasn't purchased
        # pylint: disable=no-member
        purchased_ids = order_item_model.objects.filter(
            order__user=self.user
        ).values_list('product_id', flat=True)

        # pylint: disable=no-member
        recommendations = product_model.objects.filter(
            is_active=True,
            category_id__in=preferred_categories
        ).exclude(
            id__in=purchased_ids
        ).annotate(
            avg_review=Avg('reviews__rating')
        ).order_by('-avg_review', '-created_at')[:limit]

        result = [
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'price': str(p.price),
                'image': p.image.url if p.image else None,
                'category': p.category.name if p.category else None,
                'reason': 'Based on your preferences',
            }
            for p in recommendations
        ]

        cache.set(cache_key, result, 1800)  # 30 min cache for personalized
        return result

    def get_trending_products(self, limit: int = 12) -> List[dict]:
        """
        Get trending products based on recent orders and views.
        """
        cache_key = f'trending_products_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # pylint: disable=invalid-name
        product_model = self._get_model('Product')
        order_item_model = self._get_model('OrderItem')

        # Get products ordered in the last 7 days
        week_ago = timezone.now() - timedelta(days=7)

        # pylint: disable=no-member
        trending_ids = order_item_model.objects.filter(
            order__created_at__gte=week_ago
        ).values('product_id').annotate(
            order_count=Count('product_id')
        ).order_by('-order_count')[:limit]

        product_ids = [item['product_id'] for item in trending_ids]

        if not product_ids:
            # Fallback to newest products
            # pylint: disable=no-member
            products = product_model.objects.filter(
                is_active=True
            ).order_by('-created_at')[:limit]
        else:
            # pylint: disable=no-member
            products = product_model.objects.filter(
                id__in=product_ids,
                is_active=True
            )

        result = [
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'price': str(p.price),
                'image': p.image.url if p.image else None,
                'category': p.category.name if p.category else None,
                'badge': 'Trending',
            }
            for p in products
        ]

        cache.set(cache_key, result, self.CACHE_TIMEOUT)
        return result

    def get_price_drop_alerts(self) -> List[dict]:
        """
        Get products in user's wishlist that have had price drops.
        """
        if not self.user or not self.user.is_authenticated:
            return []

        # pylint: disable=invalid-name
        wishlist_model = self._get_model('Wishlist')

        # Get wishlist products where price < MRP
        # pylint: disable=no-member
        wishlist_items = wishlist_model.objects.filter(
            user=self.user
        ).select_related('product')

        alerts = []
        for item in wishlist_items:
            product = item.product
            if product.mrp and product.price < product.mrp:
                discount = ((product.mrp - product.price) / product.mrp) * 100
                alerts.append({
                    'id': product.id,
                    'name': product.name,
                    'slug': product.slug,
                    'price': str(product.price),
                    'original_price': str(product.mrp),
                    'discount_percent': round(discount, 1),
                    'image': product.image.url if product.image else None,
                })

        return alerts

    def get_restock_suggestions(self) -> List[dict]:
        """
        Suggest products for reorder based on purchase frequency.
        """
        if not self.user or not self.user.is_authenticated:
            return []

        # pylint: disable=invalid-name
        order_item_model = self._get_model('OrderItem')
        product_model = self._get_model('Product')

        # Find products user has ordered multiple times
        # pylint: disable=no-member
        frequent_purchases = order_item_model.objects.filter(
            order__user=self.user
        ).values('product_id').annotate(
            purchase_count=Count('product_id')
        ).filter(
            purchase_count__gte=2
        ).order_by('-purchase_count')[:10]

        product_ids = [item['product_id'] for item in frequent_purchases]
        # pylint: disable=no-member
        products = product_model.objects.filter(
            id__in=product_ids,
            is_active=True
        )

        return [
            {
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'price': str(p.price),
                'image': p.image.url if p.image else None,
                'reason': 'You frequently order this',
            }
            for p in products
        ]


class SearchSuggestionEngine:
    """
    Provides search autocomplete and suggestion functionality.
    """

    def __init__(self):
        self.cache_timeout = 3600

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

    def get_suggestions(self, query: str, limit: int = 10) -> dict:
        """
        Get search suggestions based on query.
        Returns products, categories, and vendors matching the query.
        """
        if len(query) < 2:
            return {'products': [], 'categories': [], 'vendors': []}

        cache_key = f'search_suggestions_{query.lower()}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # pylint: disable=invalid-name
        product_model = self._get_model('Product')
        category_model = self._get_model('Category')
        vendor_model = self._get_model('Vendor')

        # Product suggestions
        # pylint: disable=no-member
        products = product_model.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ).values('id', 'name', 'slug')[:limit]

        # Category suggestions
        # pylint: disable=no-member
        categories = category_model.objects.filter(
            name__icontains=query
        ).values('id', 'name', 'slug')[:5]

        # Vendor suggestions
        # pylint: disable=no-member
        vendors = vendor_model.objects.filter(
            name__icontains=query
        ).values('id', 'name', 'slug')[:5]

        result = {
            'products': list(products),
            'categories': list(categories),
            'vendors': list(vendors),
        }

        cache.set(cache_key, result, self.cache_timeout)
        return result

    def get_popular_searches(self, limit: int = 10) -> List[str]:
        """
        Get popular search terms.
        This would typically be tracked via search logs.
        """
        # Placeholder - would integrate with search tracking
        return [
            'organic fertilizer',
            'hybrid seeds',
            'pesticides',
            'drip irrigation',
            'tractor parts',
            'wheat seeds',
            'tomato seeds',
            'neem oil',
            'potash fertilizer',
            'sprayer pump',
        ][:limit]
