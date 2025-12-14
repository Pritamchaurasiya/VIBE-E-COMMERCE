"""
Celery tasks for the VIBE E-Commerce store.

This module provides background task definitions for various
store operations like stock alerts, email notifications, and analytics.
"""
# pylint: disable=no-member

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Sum, Avg, F
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

# Check if Celery is available
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

    def shared_task(*_args, **_kwargs):
        """Dummy decorator when Celery is not installed."""
        def decorator(func):
            return func
        return decorator


@shared_task
def check_low_stock_alerts():
    """Check for products with low stock and send alerts."""
    from .models import Product, Notification

    low_stock_products = Product.objects.filter(
        is_active=True,
        stock_quantity__lte=10
    ).select_related('vendor')

    for product in low_stock_products:
        if product.vendor and product.vendor.user:
            Notification.objects.get_or_create(
                user=product.vendor.user,
                notification_type='stock',
                title=f'Low Stock Alert: {product.name}',
                defaults={
                    'message': f'Product "{product.name}" has only '
                               f'{product.stock_quantity} items left.',
                    'priority': 'high',
                    'link': f'/admin/store/product/{product.id}/change/'
                }
            )

    logger.info("Checked %d low stock products", low_stock_products.count())
    return f"Found {low_stock_products.count()} products with low stock"


@shared_task
def clean_expired_sessions():
    """Clean expired sessions from the database."""
    from django.contrib.sessions.models import Session

    expired_count = Session.objects.filter(
        expire_date__lt=timezone.now()
    ).delete()[0]

    logger.info("Cleaned %d expired sessions", expired_count)
    return f"Cleaned {expired_count} expired sessions"


@shared_task
def update_vendor_analytics():
    """Update analytics for all vendors."""
    from .models import Vendor, VendorAnalytics, OrderItem, Product, Review, BulkOrder

    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    for vendor in Vendor.objects.all():
        # Product stats
        products = Product.objects.filter(vendor=vendor)
        total_products = products.count()
        active_products = products.filter(is_active=True).count()
        out_of_stock_products = products.filter(stock_quantity=0).count()
        low_stock_products = products.filter(
            stock_quantity__lte=F('low_stock_threshold'),
            stock_quantity__gt=0
        ).count()

        # Order and revenue stats
        order_items = OrderItem.objects.filter(vendor=vendor, order__paid=True)
        total_orders = order_items.values('order').distinct().count()
        total_revenue = order_items.aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0

        monthly_revenue = order_items.filter(
            order__created_at__gte=thirty_days_ago
        ).aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0

        weekly_revenue = order_items.filter(
            order__created_at__gte=seven_days_ago
        ).aggregate(
            total=Sum(F('price') * F('quantity'))
        )['total'] or 0

        # Review stats
        reviews = Review.objects.filter(product__vendor=vendor)
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        total_reviews = reviews.count()

        # Bulk order stats
        pending_bulk_orders = BulkOrder.objects.filter(
            vendor=vendor, status='pending'
        ).count()

        # Top selling products
        top_selling_products = list(order_items.values(
            'product__name', 'product__slug'
        ).annotate(
            total_sold=Sum('quantity')
        ).order_by('-total_sold')[:5])


        VendorAnalytics.objects.update_or_create(
            vendor=vendor,
            date=today,
            defaults={
                'total_products': total_products,
                'active_products': active_products,
                'out_of_stock_products': out_of_stock_products,
                'low_stock_products': low_stock_products,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'monthly_revenue': monthly_revenue,
                'weekly_revenue': weekly_revenue,
                'average_rating': avg_rating,
                'total_reviews': total_reviews,
                'pending_bulk_orders': pending_bulk_orders,
                'top_selling_products': top_selling_products,
            }
        )

    logger.info("Updated vendor analytics")
    return "Vendor analytics updated successfully"


@shared_task
def send_order_confirmation_email(order_id):
    """Send order confirmation email to customer."""
    from .models import Order

    try:
        order = Order.objects.get(id=order_id)

        send_mail(
            subject=f"Order Confirmation - #{order.id}",
            message=f"""
Dear {order.first_name},

Thank you for your order!

Order Number: #{order.id}
Total Amount: ₹{order.paid_amount}

We will notify you when your order is shipped.

Best regards,
The VIBE E-Commerce Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=True
        )

        logger.info("Sent order confirmation for order #%d", order.id)
        return f"Order confirmation sent for order #{order.id}"

    except Order.DoesNotExist:
        logger.error("Order #%d not found", order_id)
        return f"Order #{order_id} not found"


@shared_task
def send_shipping_notification(order_id):
    """Send shipping notification to customer."""
    from .models import Order

    try:
        order = Order.objects.get(id=order_id)

        send_mail(
            subject=f"Your Order #{order.id} Has Been Shipped!",
            message=f"""
Dear {order.first_name},

Great news! Your order #{order.id} has been shipped!

Shipping Address:
{order.address}
{order.place}, {order.zipcode}

You can track your order status on our website.

Best regards,
The VIBE E-Commerce Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=True
        )

        logger.info("Sent shipping notification for order #%d", order.id)
        return f"Shipping notification sent for order #{order.id}"

    except Order.DoesNotExist:
        logger.error("Order #%d not found", order_id)
        return f"Order #{order_id} not found"


@shared_task
def generate_daily_report():
    """Generate daily sales report for admin."""
    from .models import Order

    user_model = get_user_model()
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    orders = Order.objects.filter(
        created_at__date=yesterday,
        paid=True
    )

    total_orders = orders.count()
    total_revenue = orders.aggregate(total=Sum('paid_amount'))['total'] or 0

    report = f"""
Daily Sales Report - {yesterday}
================================

Total Orders: {total_orders}
Total Revenue: ₹{total_revenue}

Have a great day!
The VIBE E-Commerce System
    """

    admins = user_model.objects.filter(is_superuser=True, is_active=True)

    for admin in admins:
        if admin.email:
            send_mail(
                subject=f"Daily Sales Report - {yesterday}",
                message=report,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email],
                fail_silently=True
            )

    logger.info("Generated daily report for %s", yesterday)
    return f"Daily report generated for {yesterday}"
