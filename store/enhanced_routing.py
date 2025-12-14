"""
Enhanced WebSocket URL Routing for Advanced Monitoring Features.

This module provides WebSocket URL patterns for the enhanced monitoring system,
supporting:
- Real-time system metrics
- Anomaly detection alerts
- Predictive analytics
- Multi-client synchronization

Usage:
    Add to your asgi.py or routing configuration:

    from store.enhanced_routing import enhanced_websocket_urlpatterns

    application = ProtocolTypeRouter({
        "websocket": AuthMiddlewareStack(
            URLRouter(enhanced_websocket_urlpatterns)
        ),
    })
"""

from django.urls import path

# Try to import enhanced consumers, handling channels not installed
try:
    from .enhanced_consumers import CHANNELS_AVAILABLE

    if CHANNELS_AVAILABLE:
        from .enhanced_consumers import EnhancedMonitoringConsumer
        enhanced_websocket_urlpatterns = [
            path('ws/enhanced-monitoring/', EnhancedMonitoringConsumer.as_asgi()),
            # Future routes can be added here:
            # path('ws/alerts/', AlertsConsumer.as_asgi()),
            # path('ws/analytics/', AnalyticsConsumer.as_asgi()),
        ]
    else:
        enhanced_websocket_urlpatterns = []

except (ImportError, AttributeError) as e:
    # Channels not installed or enhanced consumers not available
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("Enhanced WebSocket routing disabled: %s", e)
    enhanced_websocket_urlpatterns = []


# Export configuration for external use
__all__ = ['enhanced_websocket_urlpatterns']
