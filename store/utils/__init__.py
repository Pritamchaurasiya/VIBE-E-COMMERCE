"""
Utilities package for the store app.

This package contains utility modules for:
- Caching
- Helpers
- Constants
- Security (input validation, sanitization, rate limiting)
- Performance (query optimization, caching utilities)
"""
import logging
from decimal import Decimal
from typing import Optional, Any

from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import BadHeaderError
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.db.models import F

from ..models import Notification, Product, Order, InventoryLog, Coupon

logger = logging.getLogger(__name__)

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

def sanitize_csv_field(value: Any) -> str:
    """
    Sanitize a value for CSV export to prevent Formula Injection (CSV Injection).

    Formula injection occurs when a spreadsheet program misinterprets a cell
    starting with '=', '+', '-', or '@' as a formula.

    Args:
        value: The value to sanitize

    Returns:
        Sanitized string value
    """
    if value is None:
        return ""

    # Skip sanitization for numeric types to preserve data utility
    if isinstance(value, (int, float, Decimal)):
        return str(value)

    value_str = str(value)

    if not value_str:
        return ""

    # If the value starts with any of the dangerous characters, prepend a single quote
    # which tells Excel to treat the cell content as text.
    if value_str.startswith(('=', '+', '-', '@')):
        return f"'{value_str}"

    return value_str

def create_notification(
    user: User,
    notification_type: str,
    title: str,
    message: str,
    priority: str = 'normal',
    action_url: str = ''
) -> Notification:
    """
    Create a notification for a user.

    Args:
        user: The user to notify
        notification_type: Type of notification (order, promo, system, etc.)
        title: Notification title
        message: Notification message
        priority: Priority level (low, normal, high, urgent)
        action_url: Optional URL for the notification action

    Returns:
        The created Notification instance
    """
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        priority=priority,
        action_url=action_url
    )


def send_order_confirmation_email(order: Order) -> bool:
    """
    Send order confirmation email to customer.

    Args:
        order: The Order instance

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = f'Order Confirmation - #{order.id}'
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'items': order.items.all(),
        })
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info("Order confirmation email sent for order #%d", order.id)
        return True
    except (BadHeaderError, ConnectionError) as exc:
        logger.error("Failed to send order confirmation email: %s", exc)
        return False


def send_order_status_update_email(order: Order) -> bool:
    """
    Send order status update email to customer.

    Args:
        order: The Order instance

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = f'Order Status Update - #{order.id}'
        html_message = render_to_string('emails/order_status_update.html', {
            'order': order,
            'status': order.get_status_display(),
        })
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info("Order status update email sent for order #%d", order.id)
        return True
    except (BadHeaderError, ConnectionError) as exc:
        logger.error("Failed to send order status update email: %s", exc)
        return False


def update_product_stock(
    product: Product,
    quantity_change: int,
    action: str,
    reference: str = '',
    notes: str = '',
    created_by: Optional[User] = None
) -> bool:
    """
    Update product stock with logging.

    Args:
        product: The Product instance
        quantity_change: Positive or negative quantity change
        action: Action type (add, remove, sale, return, adjustment, damaged)
        reference: Reference ID (e.g., order number)
        notes: Additional notes
        created_by: User who made the change

    Returns:
        bool: True if stock updated successfully, False otherwise
    """
    try:
        previous_stock = product.stock_quantity
        new_stock = max(0, previous_stock + quantity_change)

        product.stock_quantity = new_stock
        product.save(update_fields=['stock_quantity'])

        # Log the inventory change
        InventoryLog.objects.create(
            product=product,
            action=action,
            quantity=quantity_change,
            previous_stock=previous_stock,
            new_stock=new_stock,
            reference=reference,
            notes=notes,
            created_by=created_by
        )

        logger.info(
            "Stock updated for product %d: %d -> %d (%s)",
            product.id, previous_stock, new_stock, action
        )
        return True
    except (ValueError, AttributeError) as exc:
        logger.error("Failed to update product stock: %s", exc)
        return False


def check_low_stock_products(threshold_multiplier: float = 1.0) -> list:
    """
    Get list of products with low stock.

    Args:
        threshold_multiplier: Multiplier for low stock threshold

    Returns:
        List of products with low stock
    """
    return list(Product.objects.filter(
        is_active=True,
        stock_quantity__lte=F('low_stock_threshold') * threshold_multiplier
    ).select_related('vendor', 'category'))


def calculate_order_total(items: list, coupon=None) -> dict:
    """
    Calculate order total with optional coupon discount.

    Args:
        items: List of cart items with product and quantity
        coupon: Optional Coupon instance

    Returns:
        dict with subtotal, discount, tax, and total
    """
    subtotal = sum(
        Decimal(str(item['price'])) * item['quantity']
        for item in items
    )

    discount = Decimal('0.00')
    if coupon and coupon.is_valid:
        if coupon.discount_type == 'percent':
            discount = subtotal * (coupon.discount_value / 100)
        else:
            discount = min(coupon.discount_value, subtotal)

    # Calculate tax (assuming 18% GST for example)
    taxable_amount = subtotal - discount
    tax = taxable_amount * Decimal('0.18')

    total = taxable_amount + tax

    return {
        'subtotal': round(subtotal, 2),
        'discount': round(discount, 2),
        'tax': round(tax, 2),
        'total': round(total, 2),
        'coupon_code': coupon.code if coupon else None
    }


def get_product_recommendations(product: Product, limit: int = 8) -> list:
    """
    Get product recommendations based on category, vendor, and price.

    Args:
        product: The base product
        limit: Maximum number of recommendations

    Returns:
        List of recommended products
    """
    recommendations = []

    # Same category products
    category_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).select_related('category', 'vendor')[:4]
    recommendations.extend(category_products)

    # Same vendor products
    vendor_products = Product.objects.filter(
        vendor=product.vendor,
        is_active=True
    ).exclude(
        id=product.id
    ).exclude(
        id__in=[p.id for p in recommendations]
    ).select_related('category', 'vendor')[:2]
    recommendations.extend(vendor_products)

    # Similar price range products
    price_min = float(product.price) * 0.7
    price_max = float(product.price) * 1.3
    price_products = Product.objects.filter(
        price__gte=price_min,
        price__lte=price_max,
        is_active=True
    ).exclude(
        id=product.id
    ).exclude(
        id__in=[p.id for p in recommendations]
    ).select_related('category', 'vendor')[:2]
    recommendations.extend(price_products)

    return recommendations[:limit]


def format_currency(amount: Decimal, currency_symbol: str = '₹') -> str:
    """
    Format currency amount for display.

    Args:
        amount: The decimal amount
        currency_symbol: Currency symbol to use

    Returns:
        Formatted currency string
    """
    return f"{currency_symbol}{amount:,.2f}"


def validate_coupon(code: str, cart_total: Decimal, user=None) -> dict:  # noqa: ARG001
    """
    Validate a coupon code.

    Args:
        code: Coupon code
        cart_total: Current cart total
        user: Optional user for user-specific coupons

    Returns:
        dict with 'valid' bool and 'message' or 'coupon' object
    """
    from django.utils import timezone

    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist:
        return {'valid': False, 'message': 'Invalid coupon code'}

    now = timezone.now()

    if not coupon.is_active:
        return {'valid': False, 'message': 'This coupon is no longer active'}

    if coupon.used_count >= coupon.max_uses:
        return {'valid': False, 'message': 'This coupon has reached its usage limit'}

    if now < coupon.valid_from:
        return {'valid': False, 'message': 'This coupon is not yet valid'}

    if now > coupon.valid_until:
        return {'valid': False, 'message': 'This coupon has expired'}

    if cart_total < coupon.min_order_value:
        return {
            'valid': False,
            'message': f'Minimum order value of {format_currency(coupon.min_order_value)} required'
        }

    # Calculate discount
    if coupon.discount_type == 'percent':
        discount = cart_total * (coupon.discount_value / 100)
    else:
        discount = min(coupon.discount_value, cart_total)

    return {
        'valid': True,
        'coupon': coupon,
        'discount': round(discount, 2),
        'message': f'Coupon applied! You save {format_currency(discount)}'
    }

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
    # CSV Security
    'sanitize_csv_field',
    # Core utilities
    'create_notification',
    'send_order_confirmation_email',
    'send_order_status_update_email',
    'update_product_stock',
    'check_low_stock_products',
    'calculate_order_total',
    'get_product_recommendations',
    'format_currency',
    'validate_coupon',
]
