"""
Comprehensive Tests for Enhanced Tracking Middleware.

This module provides unit and integration tests for:
- BaseTrackingMiddleware utilities
- SilentTrackingMiddleware
- SecurityTrackingMiddleware
- PerformanceTrackingMiddleware
- DataModificationTrackingMiddleware

Test Categories:
- Unit tests for individual methods
- Integration tests for middleware flow
- Security tests for threat detection
- Thread safety tests
- Edge case tests

Author: VIBE E-Commerce Team
Version: 2.0.0
"""
# pylint: disable=no-member,protected-access

import time
import threading
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User
from django.http import HttpResponse

from store.tracking_middleware import (
    BaseTrackingMiddleware,
    SilentTrackingMiddleware,
    SecurityTrackingMiddleware,
    PerformanceTrackingMiddleware,
    DataModificationTrackingMiddleware,
    is_valid_ip_address,
    safe_truncate,
    SLOW_RESPONSE_THRESHOLD,
    MAX_CONTENT_LENGTH,
    MAX_FAILED_ATTEMPTS,
)


def get_response_mock(request):
    """Mock get_response for middleware testing."""
    return HttpResponse('OK')


# =============================================================================
# UTILITY FUNCTION TESTS
# =============================================================================


class UtilityFunctionTests(TestCase):
    """Tests for module-level utility functions."""

    def test_is_valid_ip_address_valid_ipv4(self):
        """Test valid IPv4 address validation."""
        self.assertTrue(is_valid_ip_address('192.168.1.1'))
        self.assertTrue(is_valid_ip_address('10.0.0.1'))
        self.assertTrue(is_valid_ip_address('127.0.0.1'))
        self.assertTrue(is_valid_ip_address('255.255.255.255'))

    def test_is_valid_ip_address_valid_ipv6(self):
        """Test valid IPv6 address validation."""
        self.assertTrue(is_valid_ip_address('::1'))
        self.assertTrue(is_valid_ip_address('2001:0db8:85a3:0000:0000:8a2e:0370:7334'))
        self.assertTrue(is_valid_ip_address('fe80::1'))

    def test_is_valid_ip_address_invalid(self):
        """Test invalid IP address rejection."""
        self.assertFalse(is_valid_ip_address('not-an-ip'))
        self.assertFalse(is_valid_ip_address('256.256.256.256'))
        self.assertFalse(is_valid_ip_address('192.168.1'))
        self.assertFalse(is_valid_ip_address(''))
        self.assertFalse(is_valid_ip_address(None))
        self.assertFalse(is_valid_ip_address('<script>alert(1)</script>'))

    def test_safe_truncate_normal_string(self):
        """Test normal string truncation."""
        result = safe_truncate('hello world', 5)
        self.assertEqual(result, 'hello')

    def test_safe_truncate_short_string(self):
        """Test string shorter than max length."""
        result = safe_truncate('hi', 10)
        self.assertEqual(result, 'hi')

    def test_safe_truncate_none(self):
        """Test None input."""
        result = safe_truncate(None, 10)
        self.assertEqual(result, '')

    def test_safe_truncate_empty_string(self):
        """Test empty string input."""
        result = safe_truncate('', 10)
        self.assertEqual(result, '')


# =============================================================================
# BASE TRACKING MIDDLEWARE TESTS
# =============================================================================


class BaseTrackingMiddlewareTests(TestCase):
    """Tests for BaseTrackingMiddleware utility methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.middleware = BaseTrackingMiddleware(get_response_mock)

    def test_should_skip_path_static(self):
        """Test static files are skipped."""
        self.assertTrue(self.middleware.should_skip_path('/static/css/style.css'))

    def test_should_skip_path_media(self):
        """Test media files are skipped."""
        self.assertTrue(self.middleware.should_skip_path('/media/images/photo.jpg'))

    def test_should_skip_path_favicon(self):
        """Test favicon is skipped."""
        self.assertTrue(self.middleware.should_skip_path('/favicon.ico'))

    def test_should_skip_path_normal(self):
        """Test normal paths are not skipped."""
        self.assertFalse(self.middleware.should_skip_path('/api/products/'))
        self.assertFalse(self.middleware.should_skip_path('/shop/'))

    def test_should_skip_path_empty(self):
        """Test empty path is skipped."""
        self.assertTrue(self.middleware.should_skip_path(''))

    def test_is_health_check_true(self):
        """Test health check paths are detected."""
        self.assertTrue(self.middleware.is_health_check('/health/'))
        self.assertTrue(self.middleware.is_health_check('/healthz/'))
        self.assertTrue(self.middleware.is_health_check('/ready/'))
        self.assertTrue(self.middleware.is_health_check('/alive/'))
        self.assertTrue(self.middleware.is_health_check('/ping/'))

    def test_is_health_check_false(self):
        """Test non-health check paths."""
        self.assertFalse(self.middleware.is_health_check('/api/health-data/'))
        self.assertFalse(self.middleware.is_health_check('/shop/'))

    def test_get_client_ip_direct(self):
        """Test direct IP extraction."""
        request = self.factory.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        self.assertEqual(self.middleware.get_client_ip(request), '192.168.1.1')

    def test_get_client_ip_forwarded(self):
        """Test IP from X-Forwarded-For header."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 192.168.1.1'
        self.assertEqual(self.middleware.get_client_ip(request), '10.0.0.1')

    def test_get_client_ip_invalid_forwarded(self):
        """Test invalid X-Forwarded-For falls back to REMOTE_ADDR."""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = 'invalid-ip'
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        self.assertEqual(self.middleware.get_client_ip(request), '192.168.1.1')

    def test_get_client_ip_none(self):
        """Test missing IP addresses."""
        request = self.factory.get('/')
        request.META.pop('REMOTE_ADDR', None)
        self.assertIsNone(self.middleware.get_client_ip(request))

    def test_get_user_authenticated(self):
        """Test getting authenticated user."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'  # nosec - test credential
        )
        request = self.factory.get('/')
        request.user = user
        self.assertEqual(self.middleware.get_user(request), user)

    def test_get_user_anonymous(self):
        """Test getting anonymous user."""
        request = self.factory.get('/')
        # Create a mock anonymous user
        request.user = MagicMock()
        request.user.is_authenticated = False
        self.assertIsNone(self.middleware.get_user(request))

    def test_get_user_no_user_attr(self):
        """Test getting user when request has no user attribute."""
        request = self.factory.get('/')
        # Remove user attribute
        if hasattr(request, 'user'):
            delattr(request, 'user')
        self.assertIsNone(self.middleware.get_user(request))

    def test_is_admin_path_true(self):
        """Test admin path detection."""
        self.assertTrue(self.middleware.is_admin_path('/admin/'))
        self.assertTrue(self.middleware.is_admin_path('/admin/store/product/'))

    def test_is_admin_path_false(self):
        """Test non-admin paths."""
        self.assertFalse(self.middleware.is_admin_path('/shop/'))
        self.assertFalse(self.middleware.is_admin_path('/api/admin-data/'))  # Contains 'admin' but doesn't start with /admin/


# =============================================================================
# SILENT TRACKING MIDDLEWARE TESTS
# =============================================================================


class SilentTrackingMiddlewareTests(TestCase):
    """Tests for SilentTrackingMiddleware."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.middleware = SilentTrackingMiddleware(get_response_mock)
        self.user = User.objects.create_user(
            username='silentuser',
            password='testpass123'  # nosec - test credential
        )

    @patch('store.tracking_middleware.EnhancedTrackingService.track_system_access')
    def test_process_request_sets_start_time(self, mock_track):
        """Test that process_request sets timing."""
        request = self.factory.get('/shop/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        self.middleware.process_request(request)

        self.assertTrue(hasattr(request, '_tracking_start_time'))
        self.assertIsInstance(request._tracking_start_time, float)

    @patch('store.tracking_middleware.EnhancedTrackingService.track_system_access')
    def test_process_request_skips_static(self, mock_track):
        """Test static paths are skipped."""
        request = self.factory.get('/static/css/style.css')

        result = self.middleware.process_request(request)

        self.assertIsNone(result)
        self.assertFalse(hasattr(request, '_tracking_start_time'))
        mock_track.assert_not_called()

    @patch('store.tracking_middleware.EnhancedTrackingService.track_system_access')
    def test_process_request_skips_admin(self, mock_track):
        """Test admin paths are skipped."""
        request = self.factory.get('/admin/store/product/')

        result = self.middleware.process_request(request)

        self.assertIsNone(result)
        self.assertFalse(hasattr(request, '_tracking_start_time'))
        mock_track.assert_not_called()

    @patch('store.tracking_middleware.EnhancedTrackingService.track_user_action')
    @patch('store.tracking_middleware.EnhancedTrackingService.record_performance_metric')
    def test_process_response_tracks_page_view(self, mock_perf, mock_action):
        """Test page views are tracked."""
        request = self.factory.get('/shop/')
        request._tracking_start_time = time.time() - 0.1
        request.user = self.user
        response = HttpResponse('OK')

        result = self.middleware.process_response(request, response)

        self.assertEqual(result, response)
        mock_perf.assert_called_once()
        mock_action.assert_called_once()

    @patch('store.tracking_middleware.EnhancedTrackingService.track_user_action')
    @patch('store.tracking_middleware.EnhancedTrackingService.record_performance_metric')
    def test_process_response_no_start_time(self, mock_perf, mock_action):
        """Test response without start time is handled."""
        request = self.factory.get('/shop/')
        response = HttpResponse('OK')

        result = self.middleware.process_response(request, response)

        self.assertEqual(result, response)
        mock_perf.assert_not_called()
        mock_action.assert_not_called()

    @patch('store.tracking_middleware.EnhancedTrackingService.create_alert')
    @patch('store.tracking_middleware.EnhancedTrackingService.track_system_access')
    def test_process_exception_tracks_error(self, mock_access, mock_alert):
        """Test exception tracking."""
        request = self.factory.get('/api/error/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        exception = ValueError("Test error")

        result = self.middleware.process_exception(request, exception)

        self.assertIsNone(result)  # Returns None to allow exception propagation
        mock_access.assert_called_once()
        mock_alert.assert_called_once()

    def test_determine_access_type_admin(self):
        """Test admin access type detection."""
        request = self.factory.get('/admin/store/')
        result = self.middleware._determine_access_type(request)
        self.assertEqual(result, 'admin_access')

    def test_determine_access_type_api(self):
        """Test API access type detection."""
        request = self.factory.get('/api/v1/products/')
        result = self.middleware._determine_access_type(request)
        self.assertEqual(result, 'api_access')

    def test_determine_access_type_login(self):
        """Test login access type detection."""
        request = self.factory.post('/accounts/login/')
        result = self.middleware._determine_access_type(request)
        self.assertEqual(result, 'login_attempt')

    def test_determine_access_type_logout(self):
        """Test logout access type detection."""
        request = self.factory.get('/logout/')
        result = self.middleware._determine_access_type(request)
        self.assertEqual(result, 'logout')

    def test_determine_access_type_database(self):
        """Test database access type detection."""
        request = self.factory.post('/products/create/')
        result = self.middleware._determine_access_type(request)
        self.assertEqual(result, 'database_access')

    def test_determine_access_type_page(self):
        """Test page access type detection."""
        request = self.factory.get('/shop/')
        result = self.middleware._determine_access_type(request)
        self.assertEqual(result, 'page_access')


# =============================================================================
# SECURITY TRACKING MIDDLEWARE TESTS
# =============================================================================


class SecurityTrackingMiddlewareTests(TestCase):
    """Tests for SecurityTrackingMiddleware."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.middleware = SecurityTrackingMiddleware(get_response_mock)
        # Clear failed attempts between tests
        with self.middleware._failed_attempts_lock:
            self.middleware._failed_attempts.clear()

    def tearDown(self):
        """Clean up after tests."""
        with self.middleware._failed_attempts_lock:
            self.middleware._failed_attempts.clear()

    @patch('store.tracking_middleware.InputValidator.is_suspicious_request')
    def test_process_request_normal(self, mock_suspicious):
        """Test normal requests pass through."""
        mock_suspicious.return_value = {
            'sql_injection': False,
            'xss_attempt': False,
            'path_traversal': False
        }
        request = self.factory.get('/shop/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        result = self.middleware.process_request(request)

        self.assertIsNone(result)

    @patch('store.tracking_middleware.InputValidator.is_suspicious_request')
    @patch('store.tracking_middleware.EnhancedTrackingService.track_system_access')
    def test_process_request_sql_injection(self, mock_track, mock_suspicious):
        """Test SQL injection is blocked."""
        mock_suspicious.return_value = {
            'sql_injection': True,
            'xss_attempt': False,
            'path_traversal': False
        }
        request = self.factory.get('/api/search/', {'q': "'; DROP TABLE users; --"})
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        result = self.middleware.process_request(request)

        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 403)

    @patch('store.tracking_middleware.InputValidator.is_suspicious_request')
    @patch('store.tracking_middleware.EnhancedTrackingService.track_system_access')
    def test_process_request_xss_blocked(self, mock_track, mock_suspicious):
        """Test XSS attempts are blocked."""
        mock_suspicious.return_value = {
            'sql_injection': False,
            'xss_attempt': True,
            'path_traversal': False
        }
        request = self.factory.get('/search/', {'name': "<script>alert('xss')</script>"})
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        result = self.middleware.process_request(request)

        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 403)

    @patch('store.tracking_middleware.InputValidator.is_suspicious_request')
    @patch('store.tracking_middleware.EnhancedTrackingService.track_system_access')
    def test_process_request_path_traversal(self, mock_track, mock_suspicious):
        """Test path traversal is blocked."""
        mock_suspicious.return_value = {
            'sql_injection': False,
            'xss_attempt': False,
            'path_traversal': True
        }
        request = self.factory.get('/../../etc/passwd')
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        result = self.middleware.process_request(request)

        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 403)

    @patch('store.tracking_middleware.InputValidator.is_suspicious_request')
    def test_process_request_large_content(self, mock_suspicious):
        """Test oversized requests are blocked."""
        mock_suspicious.return_value = {
            'sql_injection': False,
            'xss_attempt': False,
            'path_traversal': False
        }
        request = self.factory.post('/api/upload/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['CONTENT_LENGTH'] = str(MAX_CONTENT_LENGTH + 1)

        result = self.middleware.process_request(request)

        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 413)

    @override_settings(TESTING=False)
    def test_brute_force_lockout(self):
        """Test brute force protection with lockout."""
        ip = '10.0.0.100'

        # Simulate failed attempts
        for _ in range(MAX_FAILED_ATTEMPTS):
            self.middleware._record_failed_attempt(ip)

        # Check lockout
        self.assertTrue(self.middleware._is_locked_out(ip))

    def test_brute_force_no_lockout_under_limit(self):
        """Test no lockout under failure limit."""
        ip = '10.0.0.101'

        # Simulate fewer than max failed attempts
        for _ in range(MAX_FAILED_ATTEMPTS - 1):
            self.middleware._record_failed_attempt(ip)

        # Should not be locked out
        self.assertFalse(self.middleware._is_locked_out(ip))

    def test_brute_force_clear_attempts(self):
        """Test clearing failed attempts after success."""
        ip = '10.0.0.102'

        # Record some failed attempts
        for _ in range(3):
            self.middleware._record_failed_attempt(ip)

        # Clear attempts
        self.middleware._clear_failed_attempts(ip)

        # Verify cleared
        with self.middleware._failed_attempts_lock:
            self.assertNotIn(ip, self.middleware._failed_attempts)

    @override_settings(ALLOWED_HOSTS=['example.com'])
    def test_csrf_suspicious_wrong_referer(self):
        """Test CSRF detection with wrong referer."""
        request = self.factory.post('/api/checkout/')
        request.META['HTTP_REFERER'] = 'http://evil.com/attack'
        user = User.objects.create_user(
            username='csrfuser',
            password='testpass123'  # nosec - test credential
        )
        request.user = user

        self.assertTrue(self.middleware._is_csrf_suspicious(request))

    @override_settings(ALLOWED_HOSTS=['example.com'])
    def test_csrf_suspicious_valid_referer(self):
        """Test CSRF detection with valid referer."""
        request = self.factory.post('/api/checkout/')
        request.META['HTTP_REFERER'] = 'https://example.com/cart/'
        user = User.objects.create_user(
            username='csrfuser2',
            password='testpass123'  # nosec - test credential
        )
        request.user = user

        self.assertFalse(self.middleware._is_csrf_suspicious(request))

    def test_csrf_suspicious_get_request(self):
        """Test GET requests are not CSRF suspicious."""
        request = self.factory.get('/shop/')
        self.assertFalse(self.middleware._is_csrf_suspicious(request))

    def test_process_response_records_failed_login(self):
        """Test failed login attempts are recorded."""
        ip = '10.0.0.200'
        request = self.factory.post('/accounts/login/')
        request.META['REMOTE_ADDR'] = ip
        response = HttpResponse(status=401)

        self.middleware.process_response(request, response)

        with self.middleware._failed_attempts_lock:
            self.assertIn(ip, self.middleware._failed_attempts)
            self.assertEqual(self.middleware._failed_attempts[ip][0], 1)

    def test_process_response_clears_on_success(self):
        """Test successful login clears failed attempts."""
        ip = '10.0.0.201'

        # First record some failures
        for _ in range(2):
            self.middleware._record_failed_attempt(ip)

        # Then simulate successful login
        request = self.factory.post('/accounts/login/')
        request.META['REMOTE_ADDR'] = ip
        response = HttpResponse(status=302)  # Redirect on success

        self.middleware.process_response(request, response)

        with self.middleware._failed_attempts_lock:
            self.assertNotIn(ip, self.middleware._failed_attempts)


class SecurityMiddlewareThreadSafetyTests(TestCase):
    """Thread safety tests for SecurityTrackingMiddleware."""

    def setUp(self):
        """Set up test fixtures."""
        self.middleware = SecurityTrackingMiddleware(get_response_mock)
        with self.middleware._failed_attempts_lock:
            self.middleware._failed_attempts.clear()

    def tearDown(self):
        """Clean up after tests."""
        with self.middleware._failed_attempts_lock:
            self.middleware._failed_attempts.clear()

    def test_concurrent_failed_attempts(self):
        """Test thread safety of failed attempt recording."""
        results = []
        errors = []

        def record_attempts(ip_suffix):
            try:
                ip = f'10.0.0.{ip_suffix}'
                for _ in range(3):
                    self.middleware._record_failed_attempt(ip)
                results.append(ip)
            except Exception as e:  # pylint: disable=broad-except
                errors.append(str(e))

        threads = [
            threading.Thread(target=record_attempts, args=(i,))
            for i in range(10)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Thread errors: {errors}")
        self.assertEqual(len(results), 10)

    @override_settings(TESTING=False)
    def test_concurrent_lockout_checks(self):
        """Test thread safety of lockout checking."""
        ip = '10.0.0.99'

        # Set up lockout
        for _ in range(MAX_FAILED_ATTEMPTS):
            self.middleware._record_failed_attempt(ip)

        results = []
        errors = []

        def check_lockout():
            try:
                is_locked = self.middleware._is_locked_out(ip)
                results.append(is_locked)
            except Exception as e:  # pylint: disable=broad-except
                errors.append(str(e))

        threads = [
            threading.Thread(target=check_lockout)
            for _ in range(20)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"Thread errors: {errors}")
        # All checks should return True
        self.assertTrue(all(results))


# =============================================================================
# PERFORMANCE TRACKING MIDDLEWARE TESTS
# =============================================================================


class PerformanceTrackingMiddlewareTests(TestCase):
    """Tests for PerformanceTrackingMiddleware."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.middleware = PerformanceTrackingMiddleware(get_response_mock)

    def test_process_request_sets_timing(self):
        """Test timing is set on request."""
        request = self.factory.get('/shop/')

        self.middleware.process_request(request)

        self.assertTrue(hasattr(request, '_perf_start_time'))
        self.assertIsInstance(request._perf_start_time, float)

    def test_process_request_sets_memory(self):
        """Test memory tracking is set."""
        request = self.factory.get('/shop/')

        self.middleware.process_request(request)

        self.assertTrue(hasattr(request, '_perf_memory_start'))

    def test_process_request_skips_static(self):
        """Test static paths are skipped."""
        request = self.factory.get('/static/js/app.js')

        self.middleware.process_request(request)

        self.assertFalse(hasattr(request, '_perf_start_time'))

    @patch('store.tracking_middleware.EnhancedTrackingService.record_performance_metric')
    def test_process_response_records_metrics(self, mock_record):
        """Test performance metrics are recorded."""
        request = self.factory.get('/shop/')
        request._perf_start_time = time.time() - 0.5
        request._perf_memory_start = 0
        response = HttpResponse('OK')

        self.middleware.process_response(request, response)

        mock_record.assert_called()

    @patch('store.tracking_middleware.EnhancedTrackingService.create_alert')
    @patch('store.tracking_middleware.EnhancedTrackingService.record_performance_metric')
    def test_process_response_alerts_slow_response(self, mock_record, mock_alert):
        """Test alerts are created for slow responses."""
        request = self.factory.get('/shop/')
        request._perf_start_time = time.time() - (SLOW_RESPONSE_THRESHOLD + 0.5)
        request._perf_memory_start = 0
        response = HttpResponse('OK')

        self.middleware.process_response(request, response)

        mock_alert.assert_called_once()

    @patch('store.tracking_middleware.EnhancedTrackingService.create_alert')
    @patch('store.tracking_middleware.EnhancedTrackingService.record_performance_metric')
    def test_process_response_no_alert_fast_response(self, mock_record, mock_alert):
        """Test no alert for fast responses."""
        request = self.factory.get('/shop/')
        request._perf_start_time = time.time() - 0.1  # 100ms
        request._perf_memory_start = 0
        response = HttpResponse('OK')

        self.middleware.process_response(request, response)

        mock_alert.assert_not_called()


# =============================================================================
# DATA MODIFICATION TRACKING MIDDLEWARE TESTS
# =============================================================================


class DataModificationTrackingMiddlewareTests(TestCase):
    """Tests for DataModificationTrackingMiddleware."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.middleware = DataModificationTrackingMiddleware(get_response_mock)

    def test_process_request_post(self):
        """Test POST requests are tracked."""
        request = self.factory.post('/api/products/')

        self.middleware.process_request(request)

        self.assertTrue(hasattr(request, '_tracking_data'))
        self.assertEqual(request._tracking_data['method'], 'POST')

    def test_process_request_put(self):
        """Test PUT requests are tracked."""
        request = self.factory.put('/api/products/1/')

        self.middleware.process_request(request)

        self.assertTrue(hasattr(request, '_tracking_data'))
        self.assertEqual(request._tracking_data['method'], 'PUT')

    def test_process_request_patch(self):
        """Test PATCH requests are tracked."""
        request = self.factory.patch('/api/products/1/')

        self.middleware.process_request(request)

        self.assertTrue(hasattr(request, '_tracking_data'))

    def test_process_request_delete(self):
        """Test DELETE requests are tracked."""
        request = self.factory.delete('/api/products/1/')

        self.middleware.process_request(request)

        self.assertTrue(hasattr(request, '_tracking_data'))

    def test_process_request_get_not_tracked(self):
        """Test GET requests are not tracked."""
        request = self.factory.get('/api/products/')

        self.middleware.process_request(request)

        self.assertFalse(hasattr(request, '_tracking_data'))

    def test_process_request_skips_admin(self):
        """Test admin paths are skipped."""
        request = self.factory.post('/admin/store/product/add/')

        self.middleware.process_request(request)

        self.assertFalse(hasattr(request, '_tracking_data'))

    @patch('store.tracking_middleware.EnhancedTrackingService.track_user_action')
    def test_process_response_tracks_success(self, mock_track):
        """Test successful modifications are tracked."""
        request = self.factory.post('/api/products/')
        request._tracking_data = {
            'method': 'POST',
            'path': '/api/products/',
            'timestamp': time.time()
        }
        request.user = MagicMock()
        request.user.is_authenticated = True
        response = HttpResponse(status=201)

        self.middleware.process_response(request, response)

        mock_track.assert_called_once()

    @patch('store.tracking_middleware.EnhancedTrackingService.track_user_action')
    def test_process_response_ignores_failure(self, mock_track):
        """Test failed modifications are not tracked."""
        request = self.factory.post('/api/products/')
        request._tracking_data = {
            'method': 'POST',
            'path': '/api/products/',
            'timestamp': time.time()
        }
        response = HttpResponse(status=400)

        self.middleware.process_response(request, response)

        mock_track.assert_not_called()

    def test_get_operation_type(self):
        """Test operation type mapping."""
        self.assertEqual(
            self.middleware._get_operation_type('POST'), 'create'
        )
        self.assertEqual(
            self.middleware._get_operation_type('PUT'), 'update'
        )
        self.assertEqual(
            self.middleware._get_operation_type('PATCH'), 'update'
        )
        self.assertEqual(
            self.middleware._get_operation_type('DELETE'), 'delete'
        )
        self.assertEqual(
            self.middleware._get_operation_type('UNKNOWN'), 'update'
        )

    def test_extract_model_name(self):
        """Test model name extraction from path."""
        self.assertEqual(
            self.middleware._extract_model_name('/products/1/'),
            'Products'
        )
        self.assertEqual(
            self.middleware._extract_model_name('/api/v1/orders/'),
            'Orders'
        )
        self.assertEqual(
            self.middleware._extract_model_name('/user-profiles/'),
            'UserProfiles'
        )
        self.assertEqual(
            self.middleware._extract_model_name(''),
            'Unknown'
        )
        self.assertEqual(
            self.middleware._extract_model_name('/'),
            'Unknown'
        )


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class MiddlewareIntegrationTests(TestCase):
    """Integration tests for middleware chain."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='integrationuser',
            password='testpass123'  # nosec - test credential
        )

    @patch('store.tracking_middleware.EnhancedTrackingService.track_system_access')
    @patch('store.tracking_middleware.EnhancedTrackingService.record_performance_metric')
    @patch('store.tracking_middleware.InputValidator.is_suspicious_request')
    def test_full_request_cycle(self, mock_suspicion, mock_perf, mock_access):
        """Test complete request/response cycle through multiple middleware."""
        mock_suspicion.return_value = {
            'sql_injection': False,
            'xss_attempt': False,
            'path_traversal': False
        }

        request = self.factory.get('/shop/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        response = HttpResponse('OK')

        # Process through all middleware
        silent_mw = SilentTrackingMiddleware(get_response_mock)
        security_mw = SecurityTrackingMiddleware(get_response_mock)
        perf_mw = PerformanceTrackingMiddleware(get_response_mock)

        # Request phase
        security_mw.process_request(request)
        silent_mw.process_request(request)
        perf_mw.process_request(request)

        # Response phase
        response = perf_mw.process_response(request, response)
        response = silent_mw.process_response(request, response)
        response = security_mw.process_response(request, response)

        self.assertEqual(response.status_code, 200)

    @patch('store.tracking_middleware.InputValidator.is_suspicious_request')
    def test_security_blocks_before_other_middleware(self, mock_suspicion):
        """Test security middleware blocks malicious requests early."""
        mock_suspicion.return_value = {
            'sql_injection': True,
            'xss_attempt': False,
            'path_traversal': False
        }

        request = self.factory.get('/api/search/', {'q': "'; DROP TABLE users;--"})
        request.META['REMOTE_ADDR'] = '192.168.1.1'

        security_mw = SecurityTrackingMiddleware(get_response_mock)

        with patch('store.tracking_middleware.EnhancedTrackingService.track_system_access'):
            result = security_mw.process_request(request)

        # Request should be blocked
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 403)

        # Other middleware should not have processed the request
        self.assertFalse(hasattr(request, '_tracking_start_time'))


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class EdgeCaseTests(TestCase):
    """Tests for edge cases and boundary conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()

    def test_empty_path_handling(self):
        """Test handling of empty or None paths."""
        middleware = BaseTrackingMiddleware(get_response_mock)

        self.assertTrue(middleware.should_skip_path(''))
        self.assertTrue(middleware.should_skip_path(None))

    def test_malformed_user_agent(self):
        """Test handling of malformed user agent strings."""
        middleware = SilentTrackingMiddleware(get_response_mock)
        request = self.factory.get('/shop/')
        request.META['HTTP_USER_AGENT'] = '\x00' * 1000  # Null bytes

        # Should not raise
        with patch('store.tracking_middleware.EnhancedTrackingService.track_system_access'):
            result = middleware.process_request(request)
        self.assertIsNone(result)

    def test_missing_meta_headers(self):
        """Test handling of requests with missing META headers."""
        middleware = SilentTrackingMiddleware(get_response_mock)
        request = self.factory.get('/shop/')
        # Clear all META except essential
        request.META = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/shop/'}

        # Should not raise
        with patch('store.tracking_middleware.EnhancedTrackingService.track_system_access'):
            result = middleware.process_request(request)
        self.assertIsNone(result)

    def test_very_long_path(self):
        """Test handling of very long URL paths."""
        middleware = DataModificationTrackingMiddleware(get_response_mock)
        long_path = '/api/v1/' + 'x' * 10000 + '/'
        request = self.factory.post(long_path)

        # Should not raise
        result = middleware.process_request(request)
        self.assertIsNone(result)

    def test_unicode_in_path(self):
        """Test handling of unicode characters in path."""
        middleware = SilentTrackingMiddleware(get_response_mock)
        request = self.factory.get('/shop/äº§å“/')  # Chinese characters

        with patch('store.tracking_middleware.EnhancedTrackingService.track_system_access'):
            result = middleware.process_request(request)
        self.assertIsNone(result)

    def test_response_without_content(self):
        """Test handling of streaming/headerless responses."""
        middleware = SilentTrackingMiddleware(get_response_mock)
        request = self.factory.get('/shop/')
        request._tracking_start_time = time.time()

        # Create a mock response that simulates missing content
        response = MagicMock()
        response.status_code = 204
        response.get = MagicMock(return_value='')
        # Simulate missing content attribute by raising AttributeError
        type(response).content = property(
            lambda self: (_ for _ in ()).throw(AttributeError('no content'))
        )

        with patch('store.tracking_middleware.EnhancedTrackingService.record_performance_metric'):
            with patch('store.tracking_middleware.EnhancedTrackingService.track_user_action'):
                result = middleware.process_response(request, response)

        self.assertEqual(result.status_code, 204)

