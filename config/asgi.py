"""
ASGI config for VIBE E-Commerce project.

It exposes the ASGI callable as a module-level variable named ``application``.

This configuration supports both HTTP and WebSocket protocols.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django ASGI application early to ensure apps are loaded
django_asgi_app = get_asgi_application()

# Import routing only after Django setup
try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from channels.security.websocket import AllowedHostsOriginValidator

    # Try to import WebSocket URL patterns
    try:
        from store.routing import websocket_urlpatterns
    except ImportError:
        websocket_urlpatterns = []

    application = ProtocolTypeRouter({
        'http': django_asgi_app,
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns)
            )
        ),
    })
except ImportError:
    # If channels is not installed, use standard ASGI application
    application = django_asgi_app
