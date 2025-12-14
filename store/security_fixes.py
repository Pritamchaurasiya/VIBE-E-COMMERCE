"""
Security Fixes Module for VIBE E-Commerce.

This module provides security utilities and fixes for common vulnerabilities.
"""

import hashlib
import secrets
import re
from typing import Optional, Dict, Any
from functools import wraps
from django.http import JsonResponse


class InputSanitizer:
    """Utility class for sanitizing user inputs."""

    # Patterns for detecting malicious input
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE)\b)",
        r"(--)|(;)|(\|\|)",
        r"(\'|\").*(\b(OR|AND)\b).*(\=)",
    ]

    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
    ]

    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e",
        r"%252e",
    ]

    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """Sanitize a string input."""
        if not value:
            return ""

        # Remove null bytes
        value = value.replace('\x00', '')

        # Truncate to max length
        value = value[:max_length]

        # HTML entity encode dangerous characters
        value = (
            value
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#x27;')
        )

        return value

    @classmethod
    def detect_sql_injection(cls, value: str) -> bool:
        """Detect potential SQL injection attempts."""
        if not value:
            return False

        value_upper = value.upper()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True
        return False

    @classmethod
    def detect_xss(cls, value: str) -> bool:
        """Detect potential XSS attempts."""
        if not value:
            return False

        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    @classmethod
    def detect_path_traversal(cls, value: str) -> bool:
        """Detect path traversal attempts."""
        if not value:
            return False

        for pattern in cls.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False

    @classmethod
    def is_safe_input(cls, value: str) -> Dict[str, bool]:
        """Check if input is safe from common attacks."""
        return {
            'sql_injection': not cls.detect_sql_injection(value),
            'xss': not cls.detect_xss(value),
            'path_traversal': not cls.detect_path_traversal(value),
        }


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = {}

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier."""
        import time
        current_time = time.time()

        if identifier not in self._requests:
            self._requests[identifier] = []

        # Clean old requests
        self._requests[identifier] = [
            t for t in self._requests[identifier]
            if current_time - t < self.window_seconds
        ]

        if len(self._requests[identifier]) >= self.max_requests:
            return False

        self._requests[identifier].append(current_time)
        return True

    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        if identifier not in self._requests:
            return self.max_requests
        return max(0, self.max_requests - len(self._requests[identifier]))


class SecureTokenGenerator:
    """Generate secure tokens for various purposes."""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_csrf_token() -> str:
        """Generate a CSRF token."""
        return secrets.token_hex(32)

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """Hash a password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        )
        return hashed.hex(), salt

    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """Verify a password against hash."""
        new_hash, _ = SecureTokenGenerator.hash_password(password, salt)
        return secrets.compare_digest(new_hash, hashed)


def require_rate_limit(max_requests: int = 100, window: int = 60):
    """Decorator to apply rate limiting to views."""
    limiter = RateLimiter(max_requests, window)

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            # Get client identifier
            identifier = (
                request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0]
                or request.META.get('REMOTE_ADDR', 'unknown')
            )

            if not limiter.is_allowed(identifier):
                return JsonResponse(
                    {'error': 'Rate limit exceeded'},
                    status=429
                )

            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def sanitize_request_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize all string values in request data."""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = InputSanitizer.sanitize_string(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_request_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                InputSanitizer.sanitize_string(v) if isinstance(v, str) else v
                for v in value
            ]
        else:
            sanitized[key] = value
    return sanitized


# SENSITIVE_FIELDS that should be redacted in logs
SENSITIVE_FIELDS = {
    'password', 'token', 'secret', 'api_key', 'apikey',
    'auth', 'credential', 'credit_card', 'ssn', 'cvv'
}


def redact_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive fields from data for logging."""
    redacted = {}
    for key, value in data.items():
        if any(field in key.lower() for field in SENSITIVE_FIELDS):
            redacted[key] = '[REDACTED]'
        elif isinstance(value, dict):
            redacted[key] = redact_sensitive_data(value)
        else:
            redacted[key] = value
    return redacted
