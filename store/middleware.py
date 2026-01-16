"""
Custom middleware for the store app.

This module provides middleware for security, logging, and performance monitoring.
"""
import logging
import time
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all incoming requests and response times.
    """

    def process_request(self, request):
        """Log the request and start the timer."""
        request._start_time = time.time()  # pylint: disable=protected-access
        logger.debug(
            "Request: %s %s from %s",
            request.method, request.path, self.get_client_ip(request)
        )

    def process_response(self, request, response):
        """Log the response and calculate request duration."""
        duration = time.time() - getattr(request, '_start_time', time.time())

        # Log slow requests (> 1 second)
        if duration > 1.0:
            logger.warning(
                "Slow request: %s %s took %.2fs",
                request.method, request.path, duration
            )

        # Add timing header for debugging
        if settings.DEBUG:
            response['X-Request-Duration'] = f"{duration:.3f}s"

        return response

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add additional security headers.
    """

    def process_response(self, _request, response):
        """Add security headers to response."""
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "frame-src https://js.stripe.com https://hooks.stripe.com;"
        )

        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions Policy
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), gyroscope=(), '
            'magnetometer=(), microphone=(), payment=*, usb=()'
        )

        # Additional Headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'

        return response


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware to enable maintenance mode.
    """

    def process_request(self, request):
        """Check if maintenance mode is enabled."""
        maintenance_mode = getattr(settings, 'MAINTENANCE_MODE', False)

        if maintenance_mode:
            # Allow admin and staff users
            if request.user.is_authenticated and request.user.is_staff:
                return None

            # Allow specific paths (login, admin)
            allowed_paths = ['/admin/', '/login/', '/api/v1/auth/']
            if any(request.path.startswith(path) for path in allowed_paths):
                return None

            # Return maintenance response
            return JsonResponse({
                'error': 'Service temporarily unavailable',
                'message': 'We are currently performing maintenance. Please try again later.'
            }, status=503)

        return None


class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware to track API versions and add deprecation warnings.
    """

    def process_response(self, request, response):
        """Add API version headers."""
        if request.path.startswith('/api/'):
            response['X-API-Version'] = '1.0.0'

            # Add deprecation warning for old API paths if needed
            # if request.path.startswith('/api/v0/'):
            #     response['X-API-Deprecated'] = 'true'
            #     response['X-API-Sunset-Date'] = '2025-01-01'

        return response


class CartSessionMiddleware(MiddlewareMixin):
    """
    Middleware to ensure cart session is properly initialized.
    """

    def process_request(self, request):
        """Initialize cart in session if not present."""
        cart_session_id = getattr(settings, 'CART_SESSION_ID', 'cart')

        if cart_session_id not in request.session:
            request.session[cart_session_id] = {}
            request.session.modified = True
