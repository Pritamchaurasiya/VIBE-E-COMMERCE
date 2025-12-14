"""
WebSocket consumers for real-time features.

This module provides WebSocket consumers for notifications,
cart updates, and order tracking using Django Channels.

Note: pylint attribute-defined-outside-init is disabled because
Django Channels consumers use connect() as the lifecycle entry point,
not __init__(). This is the standard pattern for async WebSocket consumers.
"""
# pylint: disable=no-member,attribute-defined-outside-init

import json
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

# Check if channels is available
try:
    from channels.generic.websocket import AsyncWebsocketConsumer
    from channels.db import database_sync_to_async
    CHANNELS_AVAILABLE = True
except ImportError:
    CHANNELS_AVAILABLE = False

    class AsyncWebsocketConsumer:
        """Placeholder base class when channels is not installed."""

    def database_sync_to_async(func):
        """Placeholder decorator when channels is not installed."""
        return func


if CHANNELS_AVAILABLE:

    class NotificationConsumer(AsyncWebsocketConsumer):
        """WebSocket consumer for real-time notifications."""

        async def connect(self):
            """Handle WebSocket connection."""
            self.user = self.scope.get('user')

            if not self.user or not self.user.is_authenticated:
                await self.close()
                return

            self.room_group_name = f'notifications_{self.user.id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            count = await self.get_unread_count()
            await self.send(text_data=json.dumps({
                'type': 'notification_count',
                'count': count
            }))

        async def disconnect(self, _close_code):
            """Handle WebSocket disconnection."""
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

        async def receive(self, text_data):
            """Handle incoming WebSocket messages."""
            try:
                data = json.loads(text_data)
                message_type = data.get('type')

                if message_type == 'mark_read':
                    notification_ids = data.get('ids', [])
                    await self.mark_notifications_read(notification_ids)
                    count = await self.get_unread_count()
                    await self.send(text_data=json.dumps({
                        'type': 'notification_count',
                        'count': count
                    }))
            except json.JSONDecodeError:
                logger.error("Invalid JSON received in NotificationConsumer")

        async def notification_message(self, event):
            """Send notification to WebSocket."""
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'message': event['message'],
                'title': event.get('title', ''),
                'link': event.get('link', '#')
            }))

        @database_sync_to_async
        def get_unread_count(self):
            """Get count of unread notifications."""
            from .models import Notification
            return Notification.objects.filter(
                user=self.user,
                is_read=False
            ).count()

        @database_sync_to_async
        def mark_notifications_read(self, notification_ids):
            """Mark notifications as read."""
            from .models import Notification
            Notification.objects.filter(
                user=self.user,
                id__in=notification_ids
            ).update(is_read=True)

    class CartConsumer(AsyncWebsocketConsumer):
        """WebSocket consumer for real-time cart updates."""

        async def connect(self):
            """Handle WebSocket connection."""
            self.user = self.scope.get('user')
            session = self.scope.get('session', {})
            self.session_key = session.get('session_key', 'anonymous')

            if self.user and self.user.is_authenticated:
                self.room_group_name = f'cart_{self.user.id}'
            else:
                self.room_group_name = f'cart_session_{self.session_key}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

        async def disconnect(self, _close_code):
            """Handle WebSocket disconnection."""
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

        async def cart_update(self, event):
            """Send cart update to WebSocket."""
            await self.send(text_data=json.dumps({
                'type': 'cart_update',
                'cart_count': event.get('cart_count', 0),
                'cart_total': event.get('cart_total', '0.00')
            }))

    class OrderTrackingConsumer(AsyncWebsocketConsumer):
        """WebSocket consumer for real-time order tracking."""

        async def connect(self):
            """Handle WebSocket connection."""
            self.order_id = self.scope['url_route']['kwargs']['order_id']
            self.user = self.scope.get('user')

            if not self.user or not self.user.is_authenticated:
                await self.close()
                return

            can_access = await self.verify_order_access()
            if not can_access:
                await self.close()
                return

            self.room_group_name = f'order_{self.order_id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            status = await self.get_order_status()
            await self.send(text_data=json.dumps({
                'type': 'order_status',
                'status': status
            }))

        async def disconnect(self, _close_code):
            """Handle WebSocket disconnection."""
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

        async def order_status_update(self, event):
            """Send order status update to WebSocket."""
            await self.send(text_data=json.dumps({
                'type': 'order_status',
                'status': event['status'],
                'message': event.get('message', '')
            }))

        @database_sync_to_async
        def verify_order_access(self):
            """Verify user has access to this order."""
            from .models import Order
            try:
                order = Order.objects.get(id=self.order_id)
                return order.user == self.user or self.user.is_staff
            except Order.DoesNotExist:
                return False

        @database_sync_to_async
        def get_order_status(self):
            """Get current order status."""
            from .models import Order
            try:
                order = Order.objects.get(id=self.order_id)
                return order.status
            except Order.DoesNotExist:
                return 'unknown'

    class MonitoringConsumer(AsyncWebsocketConsumer):
        """WebSocket consumer for real-time system monitoring."""

        async def connect(self):
            """Handle WebSocket connection for monitoring."""
            self.user = self.scope.get('user')

            if not self.user or not self.user.is_staff:
                await self.close()
                return

            self.room_group_name = f'monitoring_{self.user.id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            # Send initial monitoring data
            await self.send_initial_data()

        async def disconnect(self, _close_code):
            """Handle WebSocket disconnection."""
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

        async def receive(self, text_data):
            """Handle incoming monitoring commands."""
            try:
                data = json.loads(text_data)
                command = data.get('command')

                if command == 'get_metrics':
                    await self.send_metrics_data()
                elif command == 'get_logs':
                    await self.send_logs_data(data.get('level', 'info'))
                elif command == 'get_errors':
                    await self.send_errors_data()
                elif command == 'get_performance':
                    await self.send_performance_data()
            except json.JSONDecodeError:
                logger.error("Invalid JSON received in MonitoringConsumer")

        async def system_metrics_update(self, event):
            """Send system metrics update."""
            await self.send(text_data=json.dumps({
                'type': 'system_metrics',
                'data': event['data']
            }))

        async def error_alert(self, event):
            """Send error alert."""
            await self.send(text_data=json.dumps({
                'type': 'error_alert',
                'error': event['error']
            }))

        async def performance_alert(self, event):
            """Send performance alert."""
            await self.send(text_data=json.dumps({
                'type': 'performance_alert',
                'metric': event['metric']
            }))

        async def send_initial_data(self):
            """Send initial monitoring data."""
            try:
                # Get basic system metrics
                metrics_data = await self.get_system_metrics()
                await self.send(text_data=json.dumps({
                    'type': 'initial_data',
                    'metrics': metrics_data
                }))
            except Exception as e:
                logger.error("Error sending initial monitoring data: %s", e)

        async def send_metrics_data(self):
            """Send current system metrics."""
            try:
                metrics = await self.get_system_metrics()
                await self.send(text_data=json.dumps({
                    'type': 'metrics_data',
                    'metrics': metrics
                }))
            except Exception as e:
                logger.error("Error sending metrics data: %s", e)

        async def send_logs_data(self, level='info'):
            """Send recent logs."""
            try:
                logs = await self.get_recent_logs(level)
                await self.send(text_data=json.dumps({
                    'type': 'logs_data',
                    'logs': logs,
                    'level': level
                }))
            except Exception as e:
                logger.error("Error sending logs data: %s", e)

        async def send_errors_data(self):
            """Send recent errors."""
            try:
                errors = await self.get_recent_errors()
                await self.send(text_data=json.dumps({
                    'type': 'errors_data',
                    'errors': errors
                }))
            except Exception as e:
                logger.error("Error sending errors data: %s", e)

        async def send_performance_data(self):
            """Send performance metrics."""
            try:
                performance = await self.get_performance_metrics()
                await self.send(text_data=json.dumps({
                    'type': 'performance_data',
                    'performance': performance
                }))
            except Exception as e:
                logger.error("Error sending performance data: %s", e)

        @database_sync_to_async
        def get_system_metrics(self):
            """Get current system metrics."""
            try:
                from django.db import connection
                # psutil is optional for system metrics
                try:
                    import psutil
                    has_psutil = True
                except ImportError:
                    has_psutil = False

                metrics = {
                    'timestamp': timezone.now().isoformat(),
                    'database': {
                        'connections': 0,
                        'slow_queries': 0
                    },
                    'cache': {
                        'hit_ratio': 0.0,
                        'memory_usage': 0
                    },
                    'memory': {
                        'total': psutil.virtual_memory().total if has_psutil else 0,
                        'available': psutil.virtual_memory().available if has_psutil else 0,
                        'percent': psutil.virtual_memory().percent if has_psutil else 0
                    },
                    'cpu': {
                        'percent': psutil.cpu_percent(interval=0.1) if has_psutil else 0,
                        'count': psutil.cpu_count() if has_psutil else 0
                    }
                }

                # Database metrics
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT count(*) FROM pg_stat_activity
                            WHERE datname = current_database()
                        """)
                        metrics['database']['connections'] = cursor.fetchone()[0]
                except Exception:
                    metrics['database']['error'] = 'Unable to fetch DB metrics'

                return metrics
            except Exception as e:
                logger.error("Error getting system metrics: %s", e)
                return {'error': str(e)}

        @database_sync_to_async
        def get_recent_logs(self, level='info'):
            """Get recent application logs."""
            # This would integrate with your logging system
            # For now, return mock data
            return [
                {
                    'timestamp': timezone.now().isoformat(),
                    'level': level,
                    'message': f'Sample {level} log entry',
                    'module': 'store.monitoring'
                }
            ]

        @database_sync_to_async
        def get_recent_errors(self):
            """Get recent errors from the system."""
            try:
                from .models import UserActivityLog
                errors = UserActivityLog.objects.filter(
                    activity_type='error'
                ).order_by('-timestamp')[:10]

                return [
                    {
                        'timestamp': error.timestamp.isoformat(),
                        'type': error.activity_type,
                        'data': error.activity_data,
                        'user': error.user.username if error.user else 'System'
                    }
                    for error in errors
                ]
            except Exception as e:
                logger.error("Error getting recent errors: %s", e)
                return []

        @database_sync_to_async
        def get_performance_metrics(self):
            """Get current performance metrics."""
            try:
                from django.core.cache import cache


                metrics = {
                    'timestamp': timezone.now().isoformat(),
                    'response_time': 0.0,
                    'requests_per_minute': 0,
                    'database_queries_per_minute': 0,
                    'cache_hit_ratio': 0.0
                }

                try:
                    if hasattr(cache, '_cache') and hasattr(cache._cache, 'get_stats'):
                        _ = cache._cache.get_stats()  # noqa: F841
                    metrics['cache_hit_ratio'] = 85.5  # Mock data
                except Exception:
                    metrics['cache_hit_ratio'] = 0.0

                return metrics
            except Exception as e:
                logger.error("Error getting performance metrics: %s", e)
                return {'error': str(e)}

else:

    class NotificationConsumer:
        """Placeholder for NotificationConsumer when channels is not installed."""

    class CartConsumer:
        """Placeholder for CartConsumer when channels is not installed."""

    class OrderTrackingConsumer:
        """Placeholder for OrderTrackingConsumer when channels is not installed."""

    class MonitoringConsumer:
        """Placeholder for MonitoringConsumer when channels is not installed."""
