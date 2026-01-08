"""
AI-powered recommendation service for personalized product suggestions.

This module provides recommendation algorithms for:
- Similar products
- Frequently bought together
- Personalized recommendations based on user history
- Trending products
- Category-based recommendations

Note: Model imports are done inside methods to avoid circular dependencies.
This is intentional - do not move them to module level.
"""
# pylint: disable=no-member,import-outside-toplevel

import logging
from datetime import timedelta

from django.db.models import Count, Avg, Q
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Cache timeout
RECOMMENDATION_CACHE_TTL = getattr(settings, 'CACHE_TTL_MEDIUM', 1800)


class RecommendationService:
    """Service for generating product recommendations."""

    def __init__(self, user=None):
        """Initialize recommendation service for a user."""
        self.user = user

    def get_similar_products(self, product, limit=6):
        """
        Get products similar to the given product based on:
        - Same category
        - Same vendor
        - Similar price range
        - Shared attributes
        """
        from store.models import Product

        cache_key = f'similar_products_{product.id}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        similar = Product.objects.filter(
            is_active=True
        ).exclude(
            id=product.id
        ).select_related('category', 'vendor').prefetch_related('images')

        # Same category products
        if product.category:
            similar = similar.filter(
                Q(category=product.category) |
                Q(vendor=product.vendor)
            )

        # Price range filter (within 50%)
        price_min = float(product.price) * 0.5
        price_max = float(product.price) * 1.5
        similar = similar.filter(price__gte=price_min, price__lte=price_max)

        # Order by rating and then by recency
        similar = similar.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count_annotated=Count('reviews')
        ).order_by('-avg_rating', '-created_at')[:limit]

        result = list(similar)
        cache.set(cache_key, result, RECOMMENDATION_CACHE_TTL)
        return result

    def get_frequently_bought_together(self, product, limit=4):
        """
        Get products frequently purchased together based on order history.
        """
        from store.models import Product, OrderItem

        cache_key = f'bought_together_{product.id}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Find orders containing this product
        orders_with_product = OrderItem.objects.filter(
            product=product
        ).values_list('order_id', flat=True)

        # Find other products in those orders
        related_products = OrderItem.objects.filter(
            order_id__in=orders_with_product
        ).exclude(
            product=product
        ).values('product').annotate(
            frequency=Count('product')
        ).order_by('-frequency')[:limit]

        product_ids = [item['product'] for item in related_products]
        products = Product.objects.filter(
            id__in=product_ids,
            is_active=True
        ).select_related('category', 'vendor').prefetch_related('images').annotate(
            avg_rating=Avg('reviews__rating'),
            review_count_annotated=Count('reviews')
        )

        result = list(products)
        cache.set(cache_key, result, RECOMMENDATION_CACHE_TTL)
        return result

    def get_personalized_recommendations(self, limit=12):
        """
        Get personalized recommendations based on user's:
        - Purchase history
        - Wishlist
        - Browsing history
        - Reviews
        """
        from store.models import Product, Order, Wishlist

        if not self.user or not self.user.is_authenticated:
            return self.get_trending_products(limit)

        cache_key = f'personalized_{self.user.id}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Get categories and vendors from user's history
        user_orders = Order.objects.filter(user=self.user)
        purchased_products = Product.objects.filter(
            items__order__in=user_orders
        ).distinct()

        # Get categories user has purchased from
        user_categories = purchased_products.values_list(
            'category_id', flat=True
        ).distinct()

        # Get vendors user has purchased from
        user_vendors = purchased_products.values_list(
            'vendor_id', flat=True
        ).distinct()

        # Get wishlist items
        wishlist_categories = Wishlist.objects.filter(
            user=self.user
        ).values_list('product__category_id', flat=True)

        # Combine categories
        all_categories = set(user_categories) | set(wishlist_categories)

        # Exclude already purchased
        recommendations = Product.objects.filter(
            is_active=True
        ).exclude(
            id__in=purchased_products.values_list('id', flat=True)
        ).select_related('category', 'vendor').prefetch_related('images')

        if all_categories:
            recommendations = recommendations.filter(
                Q(category_id__in=all_categories) |
                Q(vendor_id__in=user_vendors)
            )

        recommendations = recommendations.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count_annotated=Count('reviews'),
            order_count=Count('items')
        ).order_by('-avg_rating', '-order_count')[:limit]

        result = list(recommendations)
        cache.set(cache_key, result, RECOMMENDATION_CACHE_TTL)
        return result

    def get_trending_products(self, limit=12, days=7):
        """
        Get trending products based on recent orders and views.
        """
        from store.models import Product

        cache_key = f'trending_products_{days}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        since = timezone.now() - timedelta(days=days)

        trending = Product.objects.filter(
            is_active=True,
            items__order__created_at__gte=since
        ).select_related('category', 'vendor').prefetch_related('images').annotate(
            recent_orders=Count('items'),
            avg_rating=Avg('reviews__rating'),
            review_count_annotated=Count('reviews')
        ).order_by('-recent_orders', '-avg_rating')[:limit]

        result = list(trending)
        cache.set(cache_key, result, RECOMMENDATION_CACHE_TTL // 2)
        return result

    def get_category_recommendations(self, category, limit=8):
        """
        Get top products in a category.
        """
        from store.models import Product

        cache_key = f'category_recs_{category.id}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        products = Product.objects.filter(
            category=category,
            is_active=True
        ).select_related('category', 'vendor').prefetch_related('images').annotate(
            avg_rating=Avg('reviews__rating'),
            review_count_annotated=Count('reviews'),
            order_count=Count('items')
        ).order_by('-avg_rating', '-order_count')[:limit]

        result = list(products)
        cache.set(cache_key, result, RECOMMENDATION_CACHE_TTL)
        return result

    def get_vendor_recommendations(self, vendor, limit=8):
        """
        Get top products from a vendor.
        """
        from store.models import Product

        cache_key = f'vendor_recs_{vendor.id}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        products = Product.objects.filter(
            vendor=vendor,
            is_active=True
        ).select_related('category', 'vendor').prefetch_related('images').annotate(
            avg_rating=Avg('reviews__rating'),
            review_count_annotated=Count('reviews'),
            order_count=Count('items')
        ).order_by('-avg_rating', '-order_count')[:limit]

        result = list(products)
        cache.set(cache_key, result, RECOMMENDATION_CACHE_TTL)
        return result

    def get_deal_recommendations(self, limit=6):
        """
        Get active deals sorted by discount and popularity.
        """
        from store.models import Deal, FlashSale

        cache_key = 'deal_recommendations'
        cached = cache.get(cache_key)
        if cached:
            return cached

        now = timezone.now()

        # Active flash sales
        flash_sales = FlashSale.objects.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now
        ).order_by('-discount_percentage')[:limit]

        # Active deals
        deals = Deal.objects.filter(
            is_active=True,
            start_date__lte=now.date(),
            end_date__gte=now.date()
        ).order_by('-discount_percentage')[:limit]

        result = {
            'flash_sales': list(flash_sales),
            'deals': list(deals)
        }
        cache.set(cache_key, result, 300)  # 5 min cache
        return result


def get_recommendations_for_cart(cart_items, limit=4):
    """
    Get recommendations based on cart contents.
    """
    from store.models import Product, OrderItem

    if not cart_items:
        return Product.objects.filter(is_active=True).order_by('-created_at')[:limit]

    product_ids = [item['product'].id for item in cart_items.values()
                   if 'product' in item]

    if not product_ids:
        return Product.objects.filter(is_active=True).order_by('-created_at')[:limit]

    # Find orders with any of these products
    orders_with_products = OrderItem.objects.filter(
        product_id__in=product_ids
    ).values_list('order_id', flat=True).distinct()

    # Find other products in those orders
    related = OrderItem.objects.filter(
        order_id__in=orders_with_products
    ).exclude(
        product_id__in=product_ids
    ).values('product').annotate(
        count=Count('product')
    ).order_by('-count')[:limit]

    related_ids = [r['product'] for r in related]
    return Product.objects.filter(
        id__in=related_ids,
        is_active=True
    ).select_related('category', 'vendor').prefetch_related('images').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count_annotated=Count('reviews')
    )


def get_seasonal_recommendations(limit=8):
    """
    Get seasonal/agricultural cycle-based recommendations.
    """
    from store.models import Product

    current_month = timezone.now().month

    # Define seasonal tags based on Indian agricultural seasons
    seasonal_tags = {
        # Kharif season (June - October)
        6: ['monsoon', 'kharif', 'rice', 'maize', 'cotton'],
        7: ['monsoon', 'kharif', 'rice', 'maize', 'cotton'],
        8: ['monsoon', 'kharif', 'rice', 'soybean'],
        9: ['kharif', 'harvest', 'pesticide'],
        10: ['harvest', 'rabi', 'preparation'],
        # Rabi season (November - March)
        11: ['rabi', 'wheat', 'mustard', 'potato'],
        12: ['rabi', 'wheat', 'barley', 'irrigation'],
        1: ['rabi', 'wheat', 'fertilizer', 'winter'],
        2: ['rabi', 'harvest', 'preparation'],
        3: ['summer', 'preparation', 'zaid'],
        # Zaid season (March - May)
        4: ['summer', 'zaid', 'watermelon', 'cucumber'],
        5: ['summer', 'zaid', 'irrigation', 'preparation'],
    }

    tags = seasonal_tags.get(current_month, [])

    if not tags:
        return Product.objects.filter(is_active=True).order_by('-created_at')[:limit]

    # Search for products matching seasonal tags
    query = Q()
    for tag in tags:
        query |= Q(name__icontains=tag) | Q(description__icontains=tag)

    products = Product.objects.filter(
        is_active=True
    ).filter(query).select_related('category', 'vendor').prefetch_related('images').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count_annotated=Count('reviews')
    ).order_by('-avg_rating')[:limit]

    # If not enough seasonal products, fill with trending
    if products.count() < limit:
        remaining = limit - products.count()
        trending = Product.objects.filter(
            is_active=True
        ).exclude(
            id__in=products.values_list('id', flat=True)
        ).select_related('category', 'vendor').prefetch_related('images').order_by('-created_at')[:remaining]
        return list(products) + list(trending)

    return list(products)
