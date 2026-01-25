"""
Django signals for the store app.

This module handles automatic actions triggered by model events.
"""
# pylint: disable=no-member,unused-argument,protected-access

import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import (
    Order, OrderItem, Product, Profile, Review, BulkOrder,
    Notification, VendorVerification, UserSession
)
from django.utils import timezone

logger = logging.getLogger(__name__)

# Constants
VENDOR_DASHBOARD_URL = '/vendor/dashboard/'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a Profile when a new User is created.
    """
    if created:
        Profile.objects.get_or_create(user=instance)
        logger.info("Profile created for user: %s", instance.username)


@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """
    Handle order status changes and notifications.
    """
    if created:
        # New order notification
        if instance.user:
            Notification.objects.create(
                user=instance.user,
                notification_type='order',
                title='Order Placed Successfully',
                message=f'Your order #{instance.id} has been placed and is being processed.',
                link=f'/orders/{instance.id}/'
            )
        logger.info("New order created: #%d", instance.id)
    else:
        # Status update notification
        if instance.user and hasattr(instance, '_previous_status'):
            if instance.status != instance._previous_status:
                Notification.objects.create(
                    user=instance.user,
                    notification_type='order',
                    title='Order Status Updated',
                    message=(
                        f'Your order #{instance.id} status has been updated '
                        f'to {instance.get_status_display()}.'
                    ),
                    link=f'/orders/{instance.id}/'
                )
                logger.info(
                    "Order #%d status changed to %s", instance.id, instance.status
                )


@receiver(pre_save, sender=Order)
def save_previous_order_status(sender, instance, **kwargs):
    """
    Save previous order status for comparison.
    """
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._previous_status = old_instance.status
        except Order.DoesNotExist:
            instance._previous_status = None


@receiver(post_save, sender=OrderItem)
def update_product_stock_on_order(sender, instance, created, **kwargs):
    """
    Update product stock when an order item is created.
    """
    if created and instance.order.paid:
        product = instance.product
        if product.stock_quantity >= instance.quantity:
            product.stock_quantity -= instance.quantity
            product.save(update_fields=['stock_quantity'])
            logger.info(
                "Stock updated for %s: -%d (Order #%d)",
                product.name, instance.quantity, instance.order.id
            )


@receiver(post_save, sender=Review)
def update_review_notification(sender, instance, created, **kwargs):
    """
    Notify vendor when a new review is posted.
    """
    if created and instance.product.vendor.created_by:
        Notification.objects.create(
            user=instance.product.vendor.created_by,
            notification_type='review',
            title='New Product Review',
            message=(
                f'{instance.user.username} left a {instance.rating}-star '
                f'review on {instance.product.name}.'
            ),
            link=f'/product/{instance.product.slug}/'
        )
        logger.info(
            "New review for %s by %s", instance.product.name, instance.user.username
        )


@receiver(post_save, sender=BulkOrder)
def bulk_order_notification(sender, instance, created, **kwargs):
    """
    Notify vendor of new bulk order requests.
    """
    if created and instance.vendor and instance.vendor.created_by:
        Notification.objects.create(
            user=instance.vendor.created_by,
            notification_type='order',
            title='New Bulk Order Request',
            message=(
                f'New bulk order request for {instance.quantity} '
                f'units of {instance.product.name}.'
            ),
            priority='high',
            link=VENDOR_DASHBOARD_URL
        )
        logger.info("New bulk order request #%d", instance.id)


@receiver(post_save, sender=VendorVerification)
def vendor_verification_status_changed(sender, instance, **kwargs):
    """
    Notify vendor when verification status changes.
    """
    if instance.vendor.created_by:
        if instance.status == 'approved':
            Notification.objects.create(
                user=instance.vendor.created_by,
                notification_type='system',
                title='Vendor Verification Approved!',
                message='Congratulations! Your vendor account has been verified.',
                priority='high',
                link=VENDOR_DASHBOARD_URL
            )
        elif instance.status == 'rejected':
            Notification.objects.create(
                user=instance.vendor.created_by,
                notification_type='system',
                title='Vendor Verification Update',
                message='Your vendor verification needs attention. Please check the details.',
                priority='high',
                link=VENDOR_DASHBOARD_URL
            )


@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, **kwargs):
    """
    Check for low stock and notify vendor.
    """
    if instance.is_low_stock and instance.vendor.created_by:
        # Check if we recently sent a notification
        recent_notification = Notification.objects.filter(
            user=instance.vendor.created_by,
            notification_type='stock',
            message__contains=instance.name,
            created_at__gte=timezone.now() - timezone.timedelta(days=1)
        ).order_by('-created_at').first()

        if not recent_notification:
            Notification.objects.create(
                user=instance.vendor.created_by,
                notification_type='stock',
                title='Low Stock Alert',
                message=(
                    f'{instance.name} is running low on stock '
                    f'({instance.stock_quantity} remaining).'
                ),
                priority='high',
                link=VENDOR_DASHBOARD_URL
            )
            logger.warning(
                "Low stock alert for %s: %d units",
                instance.name, instance.stock_quantity
            )


@receiver(post_delete, sender=Product)
def log_product_deletion(sender, instance, **kwargs):
    """
    Log product deletions.
    """
    logger.info("Product deleted: %s (ID: %d)", instance.name, instance.id)

@receiver(user_logged_in)
def check_new_device(sender, user, request, **kwargs):
    """
    Detect login from a new device/browser and notify user.
    """
    if not request:
        return

    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
    # Simple fingerprinting based on User-Agent
    # In production, use more robust fingerprinting

    # Check if this UA has been seen before for this user
    known_session = UserSession.objects.filter(
        user=user,
        user_agent__contains=user_agent
    ).exists()

    if not known_session:
        # It's a new device/browser
        Notification.objects.create(
            user=user,
            notification_type='system',
            title='New Login Detected',
            message=f'We detected a new login from {user_agent}. If this wasn\'t you, please change your password.',
            priority='high',
            is_email_sent=True # Assuming email service picks this up
        )
        logger.warning(f"New device login detected for {user.username}: {user_agent}")
