"""
Performance optimization utilities for the store application.

Provides caching helpers, query optimization, and performance monitoring tools.
"""
import time
import logging
from functools import wraps
from typing import Any, Callable, List

from django.core.cache import cache
from django.db.models import QuerySet, Prefetch

logger = logging.getLogger(__name__)


# ============================================================================
# CACHING UTILITIES
# ============================================================================

def cache_key(*args, prefix: str = "store") -> str:
    """Generate a consistent cache key from arguments."""
    key_parts = [prefix] + [str(arg) for arg in args]
    return ":".join(key_parts)


def cached_property_ttl(ttl: int = 300):
    """
    Decorator for caching expensive property calculations with TTL.

    Args:
        ttl: Time to live in seconds
    """
    def decorator(method: Callable) -> property:
        attr_name = f"_cached_{method.__name__}"
        time_attr = f"_cached_{method.__name__}_time"

        @wraps(method)
        def wrapper(self):
            now = time.time()
            cached_time = getattr(self, time_attr, 0)

            if now - cached_time > ttl or not hasattr(self, attr_name):
                result = method(self)
                setattr(self, attr_name, result)
                setattr(self, time_attr, now)
                return result

            return getattr(self, attr_name)

        return property(wrapper)
    return decorator


def cache_queryset(
    key: str,
    ttl: int = 300,
    version: int = 1
) -> Callable:
    """
    Decorator to cache queryset results.

    Args:
        key: Cache key template (can include {arg} placeholders)
        ttl: Time to live in seconds
        version: Cache version for invalidation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            cache_key_name = f"qs:{key}:v{version}"
            for i, arg in enumerate(args):
                cache_key_name = cache_key_name.replace(f"{{arg{i}}}", str(arg))
            for k, v in kwargs.items():
                cache_key_name = cache_key_name.replace(f"{{{k}}}", str(v))

            # Try to get from cache
            cached_result = cache.get(cache_key_name)
            if cached_result is not None:
                logger.debug("Cache hit: %s", cache_key_name)
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)

            # Convert queryset to list for caching
            if isinstance(result, QuerySet):
                result = list(result)

            cache.set(cache_key_name, result, ttl)
            logger.debug("Cache miss: %s", cache_key_name)

            return result

        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate all cache keys matching a pattern.

    Note: This only works with cache backends that support key scanning.
    For production, consider using Redis with SCAN command.

    Returns:
        Number of keys invalidated (0 if not supported)
    """
    # Get cache backend
    cache_backend = cache.__class__.__name__

    if hasattr(cache, 'delete_pattern'):
        # Redis cache
        return cache.delete_pattern(pattern)

    logger.warning(
        "Cache backend %s doesn't support pattern deletion",
        cache_backend
    )
    return 0


# ============================================================================
# QUERY OPTIMIZATION
# ============================================================================

def optimize_product_queryset(
    queryset: QuerySet,
    include_reviews: bool = False,
    include_images: bool = False
) -> QuerySet:
    """
    Apply optimal prefetches and select_related for product queries.

    Args:
        queryset: Base product queryset
        include_reviews: Whether to include reviews
        include_images: Whether to include product images

    Returns:
        Optimized queryset
    """
    queryset = queryset.select_related('category', 'vendor')

    prefetches = []

    if include_images:
        prefetches.append('images')

    if include_reviews:
        # Access _meta to get related model - this is the standard Django way
        reviews_field = queryset.model._meta.get_field('reviews')  # pylint: disable=protected-access
        prefetches.append(
            Prefetch(
                'reviews',
                queryset=reviews_field.related_model.objects
                    .select_related('user')
                    .order_by('-created_at')[:5]
            )
        )

    if prefetches:
        queryset = queryset.prefetch_related(*prefetches)

    return queryset


def optimize_order_queryset(queryset: QuerySet) -> QuerySet:
    """Apply optimal prefetches for order queries."""
    # Access _meta to get related model - this is the standard Django way
    items_field = queryset.model._meta.get_field('items')  # pylint: disable=protected-access
    return queryset.select_related('user').prefetch_related(
        Prefetch(
            'items',
            queryset=items_field.related_model.objects
                .select_related('product', 'vendor')
        )
    )


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

def log_slow_query(threshold_ms: float = 100):
    """
    Decorator to log functions that execute slowly.

    Args:
        threshold_ms: Threshold in milliseconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration_ms = (time.perf_counter() - start) * 1000

            if duration_ms > threshold_ms:
                logger.warning(
                    "Slow function: %s took %.2fms (threshold: %sms)",
                    func.__name__,
                    duration_ms,
                    threshold_ms
                )

            return result
        return wrapper
    return decorator


class QueryCounter:
    """Context manager to count database queries."""

    def __init__(self, name: str = "query_counter"):
        self.name = name
        self.query_count = 0
        self._connection = None
        self._initial_count = 0

    def __enter__(self):
        from django.db import connection  # pylint: disable=import-outside-toplevel
        self._connection = connection
        self._initial_count = len(connection.queries)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.query_count = len(self._connection.queries) - self._initial_count
        if self.query_count > 10:
            logger.warning(
                "[%s] High query count: %d queries",
                self.name,
                self.query_count
            )
        return False


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def batch_processor(
    items: List[Any],
    batch_size: int = 100,
    process_func: Callable = None
) -> List[Any]:
    """
    Process items in batches to manage memory and database load.

    Args:
        items: List of items to process
        batch_size: Size of each batch
        process_func: Function to apply to each batch

    Returns:
        Combined results from all batches
    """
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        if process_func:
            batch_result = process_func(batch)
            if batch_result:
                results.extend(batch_result)

    return results


def queryset_iterator(queryset: QuerySet, chunk_size: int = 1000):
    """
    Memory-efficient iteration over large querysets.

    Args:
        queryset: QuerySet to iterate
        chunk_size: Number of items to fetch at a time

    Yields:
        Items from the queryset
    """
    pk = 0
    queryset = queryset.order_by('pk')

    while True:
        chunk = list(queryset.filter(pk__gt=pk)[:chunk_size])

        if not chunk:
            break

        for item in chunk:
            yield item

        pk = chunk[-1].pk


# ============================================================================
# LAZY LOADING
# ============================================================================

class LazyObject:
    """
    Wrapper for lazy initialization of expensive objects.
    """

    def __init__(self, factory: Callable):
        self._factory = factory
        self._value = None
        self._initialized = False

    def _get_value(self):
        if not self._initialized:
            self._value = self._factory()
            self._initialized = True
        return self._value

    def __getattr__(self, name):
        return getattr(self._get_value(), name)

    def __repr__(self):
        if self._initialized:
            return repr(self._value)
        return f"<LazyObject: {self._factory}>"
