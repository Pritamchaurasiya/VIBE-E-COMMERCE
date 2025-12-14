"""
Utilities package for the store app.

This package contains utility modules for:
- Caching
- Helpers
- Constants
- Security (input validation, sanitization, rate limiting)
- Performance (query optimization, caching utilities)
"""
from .cache import (
    CACHE_TTL_SHORT,
    CACHE_TTL_MEDIUM,
    CACHE_TTL_LONG,
    CACHE_TTL_DAY,
    generate_cache_key,
    cache_result,
    invalidate_product_cache,
    invalidate_category_cache,
    invalidate_vendor_cache,
    invalidate_user_cache,
)

# Security utilities
from .security import (
    is_valid_email,
    is_valid_phone,
    is_valid_gst,
    is_valid_pan,
    sanitize_html,
    sanitize_filename,
    sanitize_search_query,
    rate_limit,
    get_client_ip,
    generate_secure_token,
    generate_verification_code,
    mask_email,
    mask_phone,
    check_password_strength,
    is_safe_file_upload,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_DOCUMENT_EXTENSIONS,
)

# Performance utilities
from .performance import (
    cache_key,
    cached_property_ttl,
    cache_queryset,
    optimize_product_queryset,
    optimize_order_queryset,
    log_slow_query,
    QueryCounter,
    batch_processor,
    queryset_iterator,
    LazyObject,
)

__all__ = [
    # Cache utilities
    'CACHE_TTL_SHORT',
    'CACHE_TTL_MEDIUM',
    'CACHE_TTL_LONG',
    'CACHE_TTL_DAY',
    'generate_cache_key',
    'cache_result',
    'invalidate_product_cache',
    'invalidate_category_cache',
    'invalidate_vendor_cache',
    'invalidate_user_cache',
    # Security utilities
    'is_valid_email',
    'is_valid_phone',
    'is_valid_gst',
    'is_valid_pan',
    'sanitize_html',
    'sanitize_filename',
    'sanitize_search_query',
    'rate_limit',
    'get_client_ip',
    'generate_secure_token',
    'generate_verification_code',
    'mask_email',
    'mask_phone',
    'check_password_strength',
    'is_safe_file_upload',
    'ALLOWED_IMAGE_EXTENSIONS',
    'ALLOWED_DOCUMENT_EXTENSIONS',
    # Performance utilities
    'cache_key',
    'cached_property_ttl',
    'cache_queryset',
    'optimize_product_queryset',
    'optimize_order_queryset',
    'log_slow_query',
    'QueryCounter',
    'batch_processor',
    'queryset_iterator',
    'LazyObject',
]
