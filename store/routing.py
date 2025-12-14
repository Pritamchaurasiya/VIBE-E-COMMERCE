"""
WebSocket URL routing for the store app.
"""
from django.urls import path

# Try to import consumers, but handle if channels is not installed
try:
    from . import consumers

    websocket_urlpatterns = [
        path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
        path('ws/cart/', consumers.CartConsumer.as_asgi()),
        path('ws/orders/<int:order_id>/', consumers.OrderTrackingConsumer.as_asgi()),
        path('ws/monitoring/', consumers.MonitoringConsumer.as_asgi()),
    ]
except (ImportError, AttributeError):
    # Channels not installed or consumers not available
    websocket_urlpatterns = []
