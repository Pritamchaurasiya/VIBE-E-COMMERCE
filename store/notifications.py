"""
Notification System for VIBE E-Commerce
Handles user notifications for orders, promotions, and system updates.
"""
import logging
from datetime import timedelta
from typing import List, Optional
from enum import Enum

from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications."""
    ORDER_PLACED = 'order_placed'
    ORDER_CONFIRMED = 'order_confirmed'
    ORDER_SHIPPED = 'order_shipped'
    ORDER_DELIVERED = 'order_delivered'
    ORDER_CANCELLED = 'order_cancelled'
    PRICE_DROP = 'price_drop'
    BACK_IN_STOCK = 'back_in_stock'
    NEW_MESSAGE = 'new_message'
    PROMOTION = 'promotion'
    FLASH_SALE = 'flash_sale'
    REVIEW_REQUEST = 'review_request'
    PAYMENT_RECEIVED = 'payment_received'
    SECURITY_ALERT = 'security_alert'
    SYSTEM = 'system'


class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    URGENT = 'urgent'


class NotificationService:
    """
    Service for creating, managing, and delivering notifications.
    """

    NOTIFICATION_ICONS = {
        NotificationType.ORDER_PLACED: '📦',
        NotificationType.ORDER_CONFIRMED: '✅',
        NotificationType.ORDER_SHIPPED: '🚚',
        NotificationType.ORDER_DELIVERED: '🎉',
        NotificationType.ORDER_CANCELLED: '❌',
        NotificationType.PRICE_DROP: '💰',
        NotificationType.BACK_IN_STOCK: '📬',
        NotificationType.NEW_MESSAGE: '💬',
        NotificationType.PROMOTION: '🎁',
        NotificationType.FLASH_SALE: '⚡',
        NotificationType.REVIEW_REQUEST: '⭐',
        NotificationType.PAYMENT_RECEIVED: '💳',
        NotificationType.SECURITY_ALERT: '🔐',
        NotificationType.SYSTEM: 'ℹ️',
    }

    def __init__(self):
        self._notification_model = None

    def _get_notification_model(self):
        """Lazy load notification model to avoid circular imports."""
        if self._notification_model is None:
            # pylint: disable=import-outside-toplevel
            from store.models import Notification
            self._notification_model = Notification
        return self._notification_model

    def create_notification(
        self,
        user: User,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        link: Optional[str] = None,
        data: Optional[dict] = None,
    ):
        """
        Create a new notification for a user.

        Args:
            user: The user to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            priority: Priority level
            link: Optional link for the notification
            data: Optional additional data as JSON

        Returns:
            The created Notification object or None if failed
        """
        try:
            # pylint: disable=invalid-name
            notification_model = self._get_notification_model()

            # pylint: disable=no-member
            notification = notification_model.objects.create(
                user=user,
                notification_type=notification_type.value,
                title=title,
                message=message,
                priority=priority.value,
                icon=self.NOTIFICATION_ICONS.get(notification_type, 'ℹ️'),
                link=link or '',
                data=data or {},
            )

            # Invalidate user's notification cache
            cache.delete(f'notifications_{user.id}')
            cache.delete(f'unread_count_{user.id}')

            logger.info(
                "Created notification for user %s: %s",
                user.id, notification_type.value
            )
            return notification

        except (ValueError, TypeError, AttributeError) as e:
            logger.error("Failed to create notification: %s", e)
            return None

    def get_user_notifications(
        self,
        user: User,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[dict]:
        """
        Get notifications for a user.

        Args:
            user: The user
            unread_only: Only return unread notifications
            limit: Maximum number of notifications

        Returns:
            List of notification dictionaries
        """
        cache_key = f'notifications_{user.id}_{unread_only}_{limit}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # pylint: disable=invalid-name
        notification_model = self._get_notification_model()

        # pylint: disable=no-member
        queryset = notification_model.objects.filter(user=user)

        if unread_only:
            queryset = queryset.filter(is_read=False)

        notifications = queryset.order_by('-created_at')[:limit]

        result = [
            {
                'id': n.id,
                'type': n.notification_type,
                'title': n.title,
                'message': n.message,
                'icon': n.icon,
                'priority': n.priority,
                'link': n.link,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat(),
                'data': n.data,
            }
            for n in notifications
        ]

        cache.set(cache_key, result, 300)  # 5 min cache
        return result

    def get_unread_count(self, user: User) -> int:
        """Get count of unread notifications for a user."""
        cache_key = f'unread_count_{user.id}'
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        # pylint: disable=invalid-name
        notification_model = self._get_notification_model()

        # pylint: disable=no-member
        count = notification_model.objects.filter(
            user=user,
            is_read=False
        ).count()

        cache.set(cache_key, count, 300)
        return count

    def mark_as_read(
        self,
        user: User,
        notification_ids: Optional[List[int]] = None
    ) -> int:
        """
        Mark notifications as read.

        Args:
            user: The user
            notification_ids: Specific IDs to mark, or all if None

        Returns:
            Number of notifications marked as read
        """
        # pylint: disable=invalid-name
        notification_model = self._get_notification_model()

        # pylint: disable=no-member
        queryset = notification_model.objects.filter(user=user, is_read=False)

        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)

        count = queryset.update(is_read=True, read_at=timezone.now())

        # Invalidate cache
        cache.delete(f'notifications_{user.id}')
        cache.delete(f'unread_count_{user.id}')

        return count

    def mark_all_as_read(self, user: User) -> int:
        """Mark all notifications as read for a user."""
        return self.mark_as_read(user)

    def delete_notification(self, user: User, notification_id: int) -> bool:
        """Delete a specific notification."""
        # pylint: disable=invalid-name
        notification_model = self._get_notification_model()

        try:
            # pylint: disable=no-member
            notification = notification_model.objects.get(
                id=notification_id,
                user=user
            )
            notification.delete()

            # Invalidate cache
            cache.delete(f'notifications_{user.id}')
            cache.delete(f'unread_count_{user.id}')

            return True
        except notification_model.DoesNotExist:
            return False

    def cleanup_old_notifications(self, days: int = 30) -> int:
        """
        Delete notifications older than specified days.

        Args:
            days: Number of days to keep notifications

        Returns:
            Number of deleted notifications
        """
        # pylint: disable=invalid-name
        notification_model = self._get_notification_model()

        cutoff_date = timezone.now() - timedelta(days=days)
        # pylint: disable=no-member
        deleted, _ = notification_model.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).delete()

        logger.info("Cleaned up %d old notifications", deleted)
        return deleted


class OrderNotificationHelper:
    """
    Helper class for creating order-related notifications.
    """

    def __init__(self):
        self.service = NotificationService()

    def notify_order_placed(self, order) -> None:
        """Send notification when order is placed."""
        self.service.create_notification(
            user=order.user,
            notification_type=NotificationType.ORDER_PLACED,
            title='Order Placed Successfully!',
            message=f'Your order #{order.id} has been placed. '
                    f'Total: ₹{order.paid_amount}',
            priority=NotificationPriority.HIGH,
            link=f'/orders/{order.id}/',
            data={'order_id': order.id},
        )

    def notify_order_confirmed(self, order) -> None:
        """Send notification when order is confirmed."""
        self.service.create_notification(
            user=order.user,
            notification_type=NotificationType.ORDER_CONFIRMED,
            title='Order Confirmed',
            message=f'Your order #{order.id} has been confirmed by the vendor.',
            priority=NotificationPriority.NORMAL,
            link=f'/orders/{order.id}/',
            data={'order_id': order.id},
        )

    def notify_order_shipped(self, order, tracking_number: str = '') -> None:
        """Send notification when order is shipped."""
        message = f'Your order #{order.id} has been shipped!'
        if tracking_number:
            message += f' Tracking: {tracking_number}'

        self.service.create_notification(
            user=order.user,
            notification_type=NotificationType.ORDER_SHIPPED,
            title='Order Shipped! 🚚',
            message=message,
            priority=NotificationPriority.HIGH,
            link=f'/orders/{order.id}/',
            data={
                'order_id': order.id,
                'tracking_number': tracking_number,
            },
        )

    def notify_order_delivered(self, order) -> None:
        """Send notification when order is delivered."""
        self.service.create_notification(
            user=order.user,
            notification_type=NotificationType.ORDER_DELIVERED,
            title='Order Delivered! 🎉',
            message=f'Your order #{order.id} has been delivered. '
                    'Enjoy your purchase!',
            priority=NotificationPriority.HIGH,
            link=f'/orders/{order.id}/',
            data={'order_id': order.id},
        )

    def notify_order_cancelled(self, order, reason: str = '') -> None:
        """Send notification when order is cancelled."""
        message = f'Your order #{order.id} has been cancelled.'
        if reason:
            message += f' Reason: {reason}'

        self.service.create_notification(
            user=order.user,
            notification_type=NotificationType.ORDER_CANCELLED,
            title='Order Cancelled',
            message=message,
            priority=NotificationPriority.HIGH,
            link=f'/orders/{order.id}/',
            data={'order_id': order.id, 'reason': reason},
        )


class PromotionNotificationHelper:
    """
    Helper class for promotional notifications.
    """

    def __init__(self):
        self.service = NotificationService()

    def notify_price_drop(self, user: User, product, old_price, new_price) -> None:
        """Notify user of price drop on wishlist item."""
        savings = old_price - new_price
        self.service.create_notification(
            user=user,
            notification_type=NotificationType.PRICE_DROP,
            title='Price Drop Alert! 💰',
            message=f'{product.name} is now ₹{new_price} '
                    f'(was ₹{old_price}). Save ₹{savings}!',
            priority=NotificationPriority.HIGH,
            link=f'/product/{product.slug}/',
            data={
                'product_id': product.id,
                'old_price': str(old_price),
                'new_price': str(new_price),
            },
        )

    def notify_back_in_stock(self, user: User, product) -> None:
        """Notify user when wishlist item is back in stock."""
        self.service.create_notification(
            user=user,
            notification_type=NotificationType.BACK_IN_STOCK,
            title='Back in Stock! 📬',
            message=f'{product.name} is now available. '
                    'Get it before it sells out!',
            priority=NotificationPriority.HIGH,
            link=f'/product/{product.slug}/',
            data={'product_id': product.id},
        )

    def notify_flash_sale(self, users: List[User], flash_sale) -> int:
        """Notify users about a flash sale."""
        count = 0
        for user in users:
            result = self.service.create_notification(
                user=user,
                notification_type=NotificationType.FLASH_SALE,
                title=f'Flash Sale: {flash_sale.name}! ⚡',
                message=f'Save up to {flash_sale.discount_percentage}% '
                        f'for the next {flash_sale.duration_hours} hours!',
                priority=NotificationPriority.URGENT,
                link='/flash-sales/',
                data={'flash_sale_id': flash_sale.id},
            )
            if result:
                count += 1
        return count
