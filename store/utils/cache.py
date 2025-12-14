"""
Caching utilities for the store app.

This module provides caching helpers and decorators for
consistent cache key generation and invalidation patterns.
"""
import functools
import hashlib
import logging

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Cache TTL constants (in seconds)
CACHE_TTL_SHORT = getattr(settings, 'CACHE_TTL_SHORT', 300)      # 5 minutes
CACHE_TTL_MEDIUM = getattr(settings, 'CACHE_TTL_MEDIUM', 1800)   # 30 minutes
CACHE_TTL_LONG = getattr(settings, 'CACHE_TTL_LONG', 3600)       # 1 hour
CACHE_TTL_DAY = getattr(settings, 'CACHE_TTL_DAY', 86400)        # 24 hours

# Cache key prefixes
CACHE_PREFIX = 'vibe:'
PRODUCT_PREFIX = f'{CACHE_PREFIX}product:'
CATEGORY_PREFIX = f'{CACHE_PREFIX}category:'
VENDOR_PREFIX = f'{CACHE_PREFIX}vendor:'
USER_PREFIX = f'{CACHE_PREFIX}user:'
CART_PREFIX = f'{CACHE_PREFIX}cart:'
SEARCH_PREFIX = f'{CACHE_PREFIX}search:'


def generate_cache_key(*args, prefix=''):
    """
    Generate a cache key from arguments.

    Args:
        *args: Values to include in the key
        prefix: Optional prefix for the key

    Returns:
        str: Cache key string
    """
    key_parts = [str(arg) for arg in args if arg is not None]
    key_body = ':'.join(key_parts)

    # Hash long keys to stay under Redis limits
    if len(key_body) > 200:
        key_body = hashlib.sha256(key_body.encode()).hexdigest()[:32]

    return f'{prefix}{key_body}'


def get_product_cache_key(product_id):
    """Get cache key for a product."""
    return f'{PRODUCT_PREFIX}{product_id}'


def get_category_cache_key(category_id):
    """Get cache key for a category."""
    return f'{CATEGORY_PREFIX}{category_id}'


def get_vendor_cache_key(vendor_id):
    """Get cache key for a vendor."""
    return f'{VENDOR_PREFIX}{vendor_id}'


def get_user_cache_key(user_id, suffix=''):
    """Get cache key for user-specific data."""
    key = f'{USER_PREFIX}{user_id}'
    if suffix:
        key = f'{key}:{suffix}'
    return key


def get_search_cache_key(query, filters=None):
    """Get cache key for search results."""
    filter_str = ''
    if filters:
        sorted_filters = sorted(filters.items())
        filter_str = '_'.join(f'{k}={v}' for k, v in sorted_filters)

    return generate_cache_key(query, filter_str, prefix=SEARCH_PREFIX)


class CacheMixin:
    """Mixin for views that need caching utilities."""

    cache_timeout = CACHE_TTL_MEDIUM

    def get_cache_key(self, *args, **_kwargs):
        """Override to generate view-specific cache keys."""
        return generate_cache_key(
            self.__class__.__name__,
            *args,
            prefix=CACHE_PREFIX
        )

    def get_cached_data(self, cache_key):
        """Get data from cache."""
        try:
            return cache.get(cache_key)
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning("Cache get error for key %s: %s", cache_key, e)
            return None

    def set_cached_data(self, cache_key, data, timeout=None):
        """Set data in cache."""
        timeout = timeout or self.cache_timeout
        try:
            cache.set(cache_key, data, timeout)
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.warning("Cache set error for key %s: %s", cache_key, e)


def cached_property_with_ttl(ttl=CACHE_TTL_MEDIUM):
    """
    Decorator for caching property values with TTL.

    Usage:
        @cached_property_with_ttl(ttl=3600)
        def expensive_computation(self):
            return some_expensive_operation()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self):
            cache_key = f'{CACHE_PREFIX}prop:{self.__class__.__name__}:{self.pk}:{func.__name__}'
            result = cache.get(cache_key)
            if result is None:
                result = func(self)
                cache.set(cache_key, result, ttl)
            return result
        return property(wrapper)
    return decorator


def cache_result(key_func=None, timeout=CACHE_TTL_MEDIUM, prefix=''):
    """
    Decorator for caching function results.

    Args:
        key_func: Function to generate cache key from args/kwargs
        timeout: Cache TTL in seconds
        prefix: Prefix for cache key

    Usage:
        @cache_result(key_func=lambda product_id: f'product:{product_id}', timeout=3600)
        def get_product_details(product_id):
            return expensive_query()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = f'{prefix}{key_func(*args, **kwargs)}'
            else:
                cache_key = generate_cache_key(
                    func.__name__,
                    *args,
                    *kwargs.values(),
                    prefix=prefix or CACHE_PREFIX
                )

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Call function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, timeout)

            return result
        return wrapper
    return decorator


def invalidate_product_cache(product_id):
    """Invalidate all caches related to a product."""
    keys_to_delete = [
        get_product_cache_key(product_id),
        f'{PRODUCT_PREFIX}{product_id}:detail',
        f'{PRODUCT_PREFIX}{product_id}:reviews',
        f'{PRODUCT_PREFIX}{product_id}:recommendations',
    ]
    for key in keys_to_delete:
        cache.delete(key)
    logger.debug("Invalidated cache for product %d", product_id)


def invalidate_category_cache(category_id):
    """Invalidate all caches related to a category."""
    keys_to_delete = [
        get_category_cache_key(category_id),
        f'{CATEGORY_PREFIX}{category_id}:products',
    ]
    for key in keys_to_delete:
        cache.delete(key)
    logger.debug("Invalidated cache for category %d", category_id)


def invalidate_vendor_cache(vendor_id):
    """Invalidate all caches related to a vendor."""
    keys_to_delete = [
        get_vendor_cache_key(vendor_id),
        f'{VENDOR_PREFIX}{vendor_id}:products',
        f'{VENDOR_PREFIX}{vendor_id}:analytics',
    ]
    for key in keys_to_delete:
        cache.delete(key)
    logger.debug("Invalidated cache for vendor %d", vendor_id)


def invalidate_user_cache(user_id):
    """Invalidate all caches related to a user."""
    keys_to_delete = [
        get_user_cache_key(user_id),
        get_user_cache_key(user_id, 'recommendations'),
        get_user_cache_key(user_id, 'wishlist'),
        get_user_cache_key(user_id, 'orders'),
    ]
    for key in keys_to_delete:
        cache.delete(key)
    logger.debug("Invalidated cache for user %d", user_id)


def bulk_cache_get(keys):
    """
    Get multiple values from cache.

    Args:
        keys: List of cache keys

    Returns:
        dict: Mapping of key -> value (missing keys not included)
    """
    try:
        return cache.get_many(keys)
    except (ConnectionError, TimeoutError, OSError) as e:
        logger.warning("Bulk cache get error: %s", e)
        return {}


def bulk_cache_set(mapping, timeout=CACHE_TTL_MEDIUM):
    """
    Set multiple values in cache.

    Args:
        mapping: Dict of key -> value
        timeout: Cache TTL in seconds
    """
    try:
        cache.set_many(mapping, timeout)
    except (ConnectionError, TimeoutError, OSError) as e:
        logger.warning("Bulk cache set error: %s", e)


def cache_delete_pattern(pattern):
    """
    Delete all cache keys matching pattern.

    Note: This only works with Redis backend.

    Args:
        pattern: Pattern to match (e.g., 'product:*')
    """
    try:
        # Check if we're using Redis
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(f'{CACHE_PREFIX}{pattern}')
        else:
            logger.warning(
                "delete_pattern not supported with current cache backend"
            )
    except (ConnectionError, TimeoutError, OSError) as e:
        logger.warning("Cache delete pattern error: %s", e)


def warm_cache(queryset, key_func, serializer=None, timeout=CACHE_TTL_MEDIUM):
    """
    Pre-populate cache with queryset data.

    Args:
        queryset: Django queryset to cache
        key_func: Function to generate cache key from object
        serializer: Optional serializer to transform objects
        timeout: Cache TTL in seconds
    """
    mapping = {}
    for obj in queryset:
        key = key_func(obj)
        if serializer:
            value = serializer(obj).data
        else:
            value = obj
        mapping[key] = value

    if mapping:
        bulk_cache_set(mapping, timeout)
        logger.info("Warmed cache with %d items", len(mapping))
