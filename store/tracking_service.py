"""
Enhanced Tracking Service Module

This module provides a comprehensive, secure, and performant tracking service
with caching, rate limiting, input validation, and batch processing capabilities.

IMPORTANT: This module uses tracking_models.py. If you get duplicate model errors,
remove the tracking-related models from store/models.py (lines ~2360-2503).
"""

import logging
import re
import time
from collections import defaultdict
from datetime import timedelta
from functools import lru_cache
from threading import Lock
from typing import Any, Dict, List, Optional

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

# Configure logging
logger = logging.getLogger(__name__)

# Constants
CACHE_TIMEOUT = 300  # 5 minutes
CONFIG_CACHE_KEY = 'tracking_config_{category}'
RATE_LIMIT_WINDOW = 60  # seconds
MAX_REQUESTS_PER_WINDOW = 100
MAX_USER_AGENT_LENGTH = 500
BATCH_SIZE = 1000
SENSITIVE_FIELDS = frozenset({
    'password', 'token', 'secret', 'key', 'credit_card',
    'ssn', 'social_security', 'bank_account', 'cvv'
})


class RateLimiter:
    """Thread-safe rate limiter for tracking operations."""

    def __init__(self, max_requests: int = MAX_REQUESTS_PER_WINDOW,
                 window_seconds: int = RATE_LIMIT_WINDOW):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def is_allowed(self, identifier: str) -> bool:
        """Check if a request is allowed within rate limits."""
        current_time = time.time()
        window_start = current_time - self.window_seconds

        with self._lock:
            # Clean old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]

            # Check if under limit
            if len(self.requests[identifier]) < self.max_requests:
                self.requests[identifier].append(current_time)
                return True

            return False

    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests in current window."""
        current_time = time.time()
        window_start = current_time - self.window_seconds

        with self._lock:
            active_requests = [
                req_time for req_time in self.requests[identifier]
                if req_time > window_start
            ]
            return max(0, self.max_requests - len(active_requests))


class InputValidator:
    """Secure input validation for tracking data."""

    # Compiled regex patterns for efficiency
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|EXECUTE)\b|"
        r"(--|;|/\*|\*/|@@|@|char\(|nchar\(|varchar\(|nvarchar\())",
        re.IGNORECASE
    )

    XSS_PATTERN = re.compile(
        r"(<script|javascript:|vbscript:|on\w+\s*=|<iframe|<object|<embed|"
        r"<form|eval\(|document\.|window\.)",
        re.IGNORECASE
    )

    PATH_TRAVERSAL_PATTERN = re.compile(r"(\.\./|\.\.\\|%2e%2e|%252e)")

    @classmethod
    def sanitize_string(cls, value: Optional[str], max_length: int = 500) -> str:
        """Sanitize a string by removing dangerous characters."""
        if not value:
            return ''

        # Truncate to max length
        value = str(value)[:max_length]

        # Remove null bytes
        value = value.replace('\x00', '')

        # Basic HTML entity encoding for display safety
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
    def validate_ip_address(cls, ip: Optional[str]) -> Optional[str]:
        """Validate and return IP address or None."""
        if not ip:
            return None

        # Basic IP validation
        ip_pattern = re.compile(
            r'^(\d{1,3}\.){3}\d{1,3}$|^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
        )

        if ip_pattern.match(ip):
            return ip

        return None

    @classmethod
    def detect_sql_injection(cls, value: str) -> bool:
        """Detect potential SQL injection attempts."""
        if not value:
            return False
        return bool(cls.SQL_INJECTION_PATTERN.search(value))

    @classmethod
    def detect_xss(cls, value: str) -> bool:
        """Detect potential XSS attempts."""
        if not value:
            return False
        return bool(cls.XSS_PATTERN.search(value))

    @classmethod
    def detect_path_traversal(cls, path: str) -> bool:
        """Detect potential path traversal attempts."""
        if not path:
            return False
        return bool(cls.PATH_TRAVERSAL_PATTERN.search(path))

    @classmethod
    def is_suspicious_request(cls, request) -> Dict[str, bool]:
        """Check if request contains suspicious patterns."""
        results = {
            'sql_injection': False,
            'xss_attempt': False,
            'path_traversal': False
        }

        # Check GET parameters
        for value in request.GET.values():
            if isinstance(value, str):
                if cls.detect_sql_injection(value):
                    results['sql_injection'] = True
                if cls.detect_xss(value):
                    results['xss_attempt'] = True

        # Check POST parameters
        for value in request.POST.values():
            if isinstance(value, str):
                if cls.detect_sql_injection(value):
                    results['sql_injection'] = True
                if cls.detect_xss(value):
                    results['xss_attempt'] = True

        # Check path for traversal
        if cls.detect_path_traversal(request.path):
            results['path_traversal'] = True

        return results

    @classmethod
    def sanitize_metadata(cls, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata dictionary, removing sensitive information."""
        if not metadata or not isinstance(metadata, dict):
            return {}

        sanitized = {}
        for key, value in metadata.items():
            # Skip sensitive fields
            if any(sensitive in key.lower() for sensitive in SENSITIVE_FIELDS):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, str):
                sanitized[key] = cls.sanitize_string(value, 1000)
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_metadata(value)
            else:
                sanitized[key] = value

        return sanitized


class UserAgentParser:
    """Efficient user agent parsing with caching."""

    # Pre-compiled patterns
    MOBILE_PATTERN = re.compile(
        r'Mobile|Android|iPhone|iPod|BlackBerry|IEMobile',
        re.IGNORECASE
    )
    TABLET_PATTERN = re.compile(r'Tablet|iPad', re.IGNORECASE)

    BROWSER_PATTERNS = {
        'Edge': re.compile(r'Edg(e|A|iOS)?/', re.IGNORECASE),
        'Chrome': re.compile(r'Chrome/', re.IGNORECASE),
        'Firefox': re.compile(r'Firefox/', re.IGNORECASE),
        'Safari': re.compile(r'Safari/', re.IGNORECASE),
        'Opera': re.compile(r'(Opera|OPR)/', re.IGNORECASE),
        'IE': re.compile(r'(MSIE|Trident)', re.IGNORECASE),
    }

    OS_PATTERNS = {
        'Windows': re.compile(r'Windows', re.IGNORECASE),
        'macOS': re.compile(r'Mac OS X|Macintosh', re.IGNORECASE),
        'Linux': re.compile(r'Linux', re.IGNORECASE),
        'Android': re.compile(r'Android', re.IGNORECASE),
        'iOS': re.compile(r'iPhone|iPad|iPod', re.IGNORECASE),
    }

    @classmethod
    @lru_cache(maxsize=1024)
    def parse(cls, user_agent: str) -> Dict[str, str]:
        """Parse user agent string with caching."""
        if not user_agent:
            return {'device_type': 'unknown', 'browser': 'unknown', 'os': 'unknown'}

        result = {
            'device_type': 'desktop',
            'browser': 'unknown',
            'os': 'unknown'
        }

        # Detect device type
        if cls.TABLET_PATTERN.search(user_agent):
            result['device_type'] = 'tablet'
        elif cls.MOBILE_PATTERN.search(user_agent):
            result['device_type'] = 'mobile'

        # Detect browser (order matters - Edge before Chrome)
        for browser, pattern in cls.BROWSER_PATTERNS.items():
            if pattern.search(user_agent):
                result['browser'] = browser
                break

        # Detect OS
        for os_name, pattern in cls.OS_PATTERNS.items():
            if pattern.search(user_agent):
                result['os'] = os_name
                break

        return result


class EnhancedTrackingService:
    """
    Enhanced tracking service with caching, rate limiting, and security features.

    Features:
    - Configuration caching for performance
    - Rate limiting to prevent abuse
    - Input validation and sanitization
    - Batch processing for high-volume operations
    - Comprehensive error handling
    - Thread-safe operations

    Note: This service works with tracking_models.py. Import models lazily
    to avoid circular import issues.
    """

    _rate_limiter = RateLimiter()
    _pending_records: Dict[str, List[Dict]] = defaultdict(list)
    _pending_lock = Lock()

    @classmethod
    def _get_model(cls, model_name: str):
        """Lazy import of tracking models."""
        # pylint: disable=import-outside-toplevel
        from . import models
        return getattr(models, model_name)

    @classmethod
    def get_tracking_config(cls, category: str):
        """Get tracking configuration with caching."""
        cache_key = CONFIG_CACHE_KEY.format(category=category)
        config = cache.get(cache_key)

        if config is None:
            try:
                TrackingConfiguration = cls._get_model('TrackingConfiguration')
                # pylint: disable=no-member
                config = TrackingConfiguration.objects.filter(
                    category=category
                ).first()

                if config:
                    cache.set(cache_key, config, CACHE_TIMEOUT)
                else:
                    # Cache the miss to avoid repeated DB queries
                    cache.set(cache_key, False, CACHE_TIMEOUT)
                    return None
            except Exception as exc:
                logger.error("Error fetching tracking config: %s", exc)
                return None

        return config if config else None

    @classmethod
    def is_tracking_enabled(cls, category: str) -> bool:
        """Check if tracking is enabled for a category."""
        config = cls.get_tracking_config(category)
        return config.is_enabled if config else False

    @classmethod
    def invalidate_config_cache(cls, category: Optional[str] = None):
        """Invalidate configuration cache."""
        if category:
            cache.delete(CONFIG_CACHE_KEY.format(category=category))
        else:
            # Invalidate all config caches
            TrackingConfiguration = cls._get_model('TrackingConfiguration')
            for cat, _ in TrackingConfiguration.TRACKING_CATEGORIES:
                cache.delete(CONFIG_CACHE_KEY.format(category=cat))

    @classmethod
    def _extract_request_info(cls, request) -> Dict[str, Any]:
        """Extract common information from request object."""
        if not request:
            return {}

        ip_address = request.META.get('REMOTE_ADDR', '')
        # Handle X-Forwarded-For for proxied requests
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            ip_address = forwarded_for.split(',')[0].strip()

        session = getattr(request, 'session', None)
        session_id = getattr(session, 'session_key', '') if session else ''

        return {
            'ip_address': InputValidator.validate_ip_address(ip_address),
            'user_agent': InputValidator.sanitize_string(
                request.META.get('HTTP_USER_AGENT', ''),
                MAX_USER_AGENT_LENGTH
            ),
            'session_id': session_id or '',
            'path': request.path,
            'method': request.method,
        }

    @classmethod
    def track_file_operation(cls, operation: str, file_path: str,
                             user=None, request=None, **kwargs):
        """Track file operations with security checks."""
        if not cls.is_tracking_enabled('file_operations'):
            return None

        # Security check for path traversal
        if InputValidator.detect_path_traversal(file_path):
            logger.warning("Path traversal attempt: %s", file_path)
            return None

        request_info = cls._extract_request_info(request)

        try:
            import os
            SystemFileTracker = cls._get_model('SystemFileTracker')
            # pylint: disable=no-member
            return SystemFileTracker.objects.create(
                operation=operation,
                file_path=InputValidator.sanitize_string(file_path, 500),
                file_name=os.path.basename(file_path)[:255],
                file_size=kwargs.get('file_size'),
                file_type=os.path.splitext(file_path)[1].lower()[:50],
                user=user,
                ip_address=request_info.get('ip_address') or kwargs.get('ip_address'),
                user_agent=request_info.get('user_agent') or kwargs.get('user_agent', ''),
                session_id=request_info.get('session_id') or kwargs.get('session_id', ''),
                request_path=request_info.get('path') or kwargs.get('request_path', ''),
                metadata=InputValidator.sanitize_metadata(kwargs.get('metadata', {})),
                is_sensitive=kwargs.get('is_sensitive', False)
            )
        except Exception as exc:
            logger.error("Error tracking file operation: %s", exc)
            return None

    @classmethod
    def track_user_action(cls, action_type: str, user=None, request=None, **kwargs):
        """Track user actions with validation."""
        if not cls.is_tracking_enabled('user_actions'):
            return None

        request_info = cls._extract_request_info(request)

        try:
            page_url = kwargs.get('page_url', '')
            if request:
                page_url = request.build_absolute_uri()

            UserActionTracker = cls._get_model('UserActionTracker')
            # pylint: disable=no-member
            return UserActionTracker.objects.create(
                action_type=action_type,
                user=user,
                session_id=request_info.get('session_id') or kwargs.get('session_id', ''),
                ip_address=request_info.get('ip_address') or kwargs.get('ip_address'),
                user_agent=request_info.get('user_agent') or kwargs.get('user_agent', ''),
                page_url=InputValidator.sanitize_string(page_url, 200),
                page_title=InputValidator.sanitize_string(kwargs.get('page_title', ''), 255),
                element_id=InputValidator.sanitize_string(kwargs.get('element_id', ''), 100),
                element_class=InputValidator.sanitize_string(kwargs.get('element_class', ''), 100),
                duration_seconds=kwargs.get('duration_seconds'),
            )
        except Exception as exc:
            logger.error("Error tracking user action: %s", exc)
            return None

    @classmethod
    def track_system_access(cls, access_type: str, user=None, request=None, **kwargs):
        """Track system access with security analysis."""
        if not cls.is_tracking_enabled('system_access'):
            return None

        request_info = cls._extract_request_info(request)
        risk_level = kwargs.get('risk_level', 'low')

        # Check for suspicious activity
        if request:
            suspicion = InputValidator.is_suspicious_request(request)
            if any(suspicion.values()):
                risk_level = 'high'
                if suspicion.get('sql_injection'):
                    access_type = 'sql_injection'
                elif suspicion.get('xss_attempt'):
                    access_type = 'xss_attempt'

        try:
            SystemAccessTracker = cls._get_model('SystemAccessTracker')
            # pylint: disable=no-member
            return SystemAccessTracker.objects.create(
                access_type=access_type,
                user=user,
                ip_address=request_info.get('ip_address') or kwargs.get('ip_address'),
                user_agent=request_info.get('user_agent') or kwargs.get('user_agent', ''),
                session_id=request_info.get('session_id') or kwargs.get('session_id', ''),
                resource_accessed=InputValidator.sanitize_string(
                    request_info.get('path') or kwargs.get('resource_accessed', ''),
                    255
                ),
                is_successful=kwargs.get('is_successful', True),
                risk_level=risk_level,
                metadata=InputValidator.sanitize_metadata(kwargs.get('metadata', {}))
            )
        except Exception as exc:
            logger.error("Error tracking system access: %s", exc)
            return None

    @classmethod
    def record_performance_metric(cls, metric_type: str, metric_value: float,
                                   metric_unit: str, request=None, **kwargs):
        """Record performance metrics."""
        if not cls.is_tracking_enabled('performance_metrics'):
            return None

        request_info = cls._extract_request_info(request)
        user = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user

        try:
            PerformanceMetric = cls._get_model('PerformanceMetric')
            # pylint: disable=no-member
            return PerformanceMetric.objects.create(
                metric_type=metric_type,
                metric_value=metric_value,
                metric_unit=metric_unit,
                endpoint=request_info.get('path') or kwargs.get('endpoint', ''),
                user=user or kwargs.get('user'),
                session_id=request_info.get('session_id') or kwargs.get('session_id', ''),
                metadata=InputValidator.sanitize_metadata(kwargs.get('metadata', {}))
            )
        except Exception as exc:
            logger.error("Error recording performance metric: %s", exc)
            return None

    @classmethod
    def create_alert(cls, alert_type: str, title: str, description: str,
                     severity: str = 'medium', triggered_by=None, **kwargs):
        """Create a tracking alert."""
        try:
            TrackingAlert = cls._get_model('TrackingAlert')

            # Merge triggered_by into metadata
            metadata = kwargs.pop('metadata', {})
            if triggered_by:
                metadata['triggered_by'] = InputValidator.sanitize_metadata(triggered_by)

            # pylint: disable=no-member
            return TrackingAlert.objects.create(
                alert_type=alert_type,
                title=InputValidator.sanitize_string(title, 255),
                description=InputValidator.sanitize_string(description, 2000),
                severity=severity,
                metadata=metadata,
                **kwargs
            )
        except Exception as exc:
            logger.error("Error creating alert: %s", exc)
            return None

    @classmethod
    def create_security_alert(cls, threat_type: str, description: str,
                              request=None, user=None, severity: str = 'high'):
        """Create a security-specific alert."""
        request_info = cls._extract_request_info(request) if request else {}

        triggered_by = {
            'threat_type': threat_type,
            'ip_address': request_info.get('ip_address'),
            'user': user.username if user else 'anonymous',
            'path': request_info.get('path'),
            'method': request_info.get('method'),
        }

        return cls.create_alert(
            alert_type='security',
            title=f'Security Alert: {threat_type.replace("_", " ").title()}',
            description=description,
            severity=severity,
            triggered_by=triggered_by
        )

    @classmethod
    @transaction.atomic
    def cleanup_old_tracking_data(cls, batch_size: int = BATCH_SIZE) -> int:
        """Clean up old tracking data based on retention policies."""
        TrackingDataRetention = cls._get_model('TrackingDataRetention')
        # pylint: disable=no-member
        retention_policies = TrackingDataRetention.objects.filter(
            auto_cleanup_enabled=True,
            is_active=True
        )

        total_deleted = 0

        model_mapping = {
            'file_operations': ('SystemFileTracker', 'operation_timestamp'),
            'user_actions': ('UserActionTracker', 'action_timestamp'),
            'system_access': ('SystemAccessTracker', 'access_timestamp'),
            'data_modifications': ('DataModificationTracker', 'timestamp'),
            'sessions': ('SessionTracker', 'login_timestamp'),
            'performance_metrics': ('PerformanceMetric', 'timestamp'),
        }

        for policy in retention_policies:
            cutoff_date = cls._calculate_cutoff_date(
                policy.retention_period,
                policy.retention_unit
            )

            if cutoff_date is None:
                continue

            mapping = model_mapping.get(policy.data_type)
            if not mapping:
                continue

            model_name, timestamp_field = mapping
            model = cls._get_model(model_name)
            filter_kwargs = {f'{timestamp_field}__date__lt': cutoff_date}

            try:
                # Batch delete for performance
                while True:
                    ids_to_delete = list(
                        model.objects.filter(**filter_kwargs)
                        .values_list('id', flat=True)[:batch_size]
                    )

                    if not ids_to_delete:
                        break

                    deleted_count, _ = model.objects.filter(
                        id__in=ids_to_delete
                    ).delete()
                    total_deleted += deleted_count

                # Update policy timestamps
                policy.last_cleanup = timezone.now()
                policy.next_cleanup = timezone.now() + timedelta(days=1)
                policy.save(update_fields=['last_cleanup', 'next_cleanup'])

            except Exception as exc:
                logger.error("Error cleaning up %s data: %s", policy.data_type, exc)

        logger.info("Cleaned up %d old tracking records", total_deleted)
        return total_deleted

    @staticmethod
    def _calculate_cutoff_date(period: int, unit: str):
        """Calculate cutoff date for retention policy."""
        now = timezone.now().date()

        multipliers = {
            'days': 1,
            'weeks': 7,
            'months': 30,
            'years': 365,
        }

        multiplier = multipliers.get(unit)
        if multiplier is None:
            return None

        return now - timedelta(days=period * multiplier)

    @classmethod
    def get_tracking_statistics(cls) -> Dict[str, Any]:
        """Get tracking system statistics."""
        try:
            last_24h = timezone.now() - timedelta(hours=24)

            SystemFileTracker = cls._get_model('SystemFileTracker')
            UserActionTracker = cls._get_model('UserActionTracker')
            SystemAccessTracker = cls._get_model('SystemAccessTracker')
            DataModificationTracker = cls._get_model('DataModificationTracker')
            SessionTracker = cls._get_model('SessionTracker')
            TrackingAlert = cls._get_model('TrackingAlert')

            # pylint: disable=no-member
            stats = {
                'file_operations_24h': SystemFileTracker.objects.filter(
                    operation_timestamp__gte=last_24h
                ).count(),
                'user_actions_24h': UserActionTracker.objects.filter(
                    action_timestamp__gte=last_24h
                ).count(),
                'system_access_24h': SystemAccessTracker.objects.filter(
                    access_timestamp__gte=last_24h
                ).count(),
                'data_modifications_24h': DataModificationTracker.objects.filter(
                    timestamp__gte=last_24h
                ).count(),
                'active_sessions': SessionTracker.objects.filter(
                    is_active=True
                ).count(),
                'active_alerts': TrackingAlert.objects.filter(
                    status='active'
                ).count(),
                'high_risk_events_24h': SystemAccessTracker.objects.filter(
                    access_timestamp__gte=last_24h,
                    risk_level__in=['high', 'critical']
                ).count(),
            }

            return stats
        except Exception as exc:
            logger.error("Error getting tracking statistics: %s", exc)
            return {}
