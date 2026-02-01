"""
Tests for enhanced tracking system security features.

This module tests the security enhancements implemented in tracking_service.py
and tracking_middleware.py.
"""
# pylint: disable=no-member

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from django.core.cache import cache
from store.tracking_service import (
    EnhancedTrackingService,
    InputValidator,
    UserAgentParser,
    RateLimiter,
)
from .test_config import TEST_USER_PASSWORD


class InputValidatorTests(TestCase):
    """Tests for InputValidator class."""

    def test_sanitize_string_removes_null_bytes(self):
        """Test that null bytes are removed."""
        result = InputValidator.sanitize_string("hello\x00world")
        self.assertNotIn('\x00', result)

    def test_sanitize_string_truncates_to_max_length(self):
        """Test string truncation."""
        long_string = "a" * 1000
        result = InputValidator.sanitize_string(long_string, max_length=100)
        self.assertEqual(len(result), 100)

    def test_sanitize_string_escapes_html(self):
        """Test HTML escaping."""
        result = InputValidator.sanitize_string("<script>alert('xss')</script>")
        self.assertNotIn('<script>', result)
        self.assertIn('&lt;script&gt;', result)

    def test_validate_ip_address_valid_ipv4(self):
        """Test valid IPv4 address."""
        result = InputValidator.validate_ip_address("192.168.1.1")
        self.assertEqual(result, "192.168.1.1")

    def test_validate_ip_address_invalid(self):
        """Test invalid IP address."""
        result = InputValidator.validate_ip_address("not-an-ip")
        self.assertIsNone(result)

    def test_detect_sql_injection_select(self):
        """Test SQL SELECT detection."""
        self.assertTrue(InputValidator.detect_sql_injection("'; SELECT * FROM users --"))

    def test_detect_sql_injection_union(self):
        """Test SQL UNION detection."""
        self.assertTrue(InputValidator.detect_sql_injection("1 UNION SELECT password FROM users"))

    def test_detect_sql_injection_normal_text(self):
        """Test normal text does not trigger SQL detection."""
        self.assertFalse(InputValidator.detect_sql_injection("Hello World"))

    def test_detect_xss_script_tag(self):
        """Test XSS script tag detection."""
        self.assertTrue(InputValidator.detect_xss("<script>alert('xss')</script>"))

    def test_detect_xss_onerror(self):
        """Test XSS onerror detection."""
        self.assertTrue(InputValidator.detect_xss("<img onerror=alert('xss')>"))

    def test_detect_xss_normal_text(self):
        """Test normal text does not trigger XSS detection."""
        self.assertFalse(InputValidator.detect_xss("Hello World"))

    def test_detect_path_traversal(self):
        """Test path traversal detection."""
        self.assertTrue(InputValidator.detect_path_traversal("../../etc/passwd"))
        self.assertTrue(InputValidator.detect_path_traversal("%2e%2e/secret"))

    def test_detect_path_traversal_normal_path(self):
        """Test normal path does not trigger detection."""
        self.assertFalse(InputValidator.detect_path_traversal("/api/products/123"))

    def test_sanitize_metadata_redacts_sensitive(self):
        """Test sensitive field redaction."""
        # nosec B106 - Intentional test data to verify password redaction
        metadata = {
            'username': 'john',
            'password': 'secret123',  # nosec B105 - Test fixture only
            'api_key': 'abc123',
        }
        result = InputValidator.sanitize_metadata(metadata)
        self.assertEqual(result['username'], 'john')
        self.assertEqual(result['password'], '[REDACTED]')
        self.assertEqual(result['api_key'], '[REDACTED]')


class RateLimiterTests(TestCase):
    """Tests for RateLimiter class."""

    def tearDown(self):
        cache.clear()

    def test_allows_requests_under_limit(self):
        """Test requests under limit are allowed."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            self.assertTrue(limiter.is_allowed("test-ip"))

    def test_blocks_requests_over_limit(self):
        """Test requests over limit are blocked."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            limiter.is_allowed("test-ip")
        self.assertFalse(limiter.is_allowed("test-ip"))

    def test_different_identifiers_tracked_separately(self):
        """Test different IPs are tracked separately."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.is_allowed("ip-1")
        limiter.is_allowed("ip-1")
        self.assertFalse(limiter.is_allowed("ip-1"))
        self.assertTrue(limiter.is_allowed("ip-2"))

    def test_get_remaining(self):
        """Test remaining requests count."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        limiter.is_allowed("test-ip")
        self.assertEqual(limiter.get_remaining("test-ip"), 4)


class UserAgentParserTests(TestCase):
    """Tests for UserAgentParser class."""

    def test_parse_chrome_windows(self):
        """Test Chrome on Windows detection."""
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        result = UserAgentParser.parse(ua)
        self.assertEqual(result['browser'], 'Chrome')
        self.assertEqual(result['os'], 'Windows')
        self.assertEqual(result['device_type'], 'desktop')

    def test_parse_safari_macos(self):
        """Test Safari on macOS detection."""
        ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X) Safari/16.0"
        result = UserAgentParser.parse(ua)
        self.assertEqual(result['browser'], 'Safari')
        self.assertEqual(result['os'], 'macOS')

    def test_parse_mobile_android(self):
        """Test mobile Android detection."""
        ua = "Mozilla/5.0 (Linux; Android 12; Mobile) Chrome/99.0"
        result = UserAgentParser.parse(ua)
        self.assertEqual(result['device_type'], 'mobile')
        self.assertEqual(result['os'], 'Android')

    def test_parse_iphone(self):
        """Test iPhone detection."""
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0) Safari/604.1"
        result = UserAgentParser.parse(ua)
        self.assertEqual(result['device_type'], 'mobile')
        self.assertEqual(result['os'], 'iOS')

    def test_parse_ipad(self):
        """Test iPad detection (tablet)."""
        ua = "Mozilla/5.0 (iPad; CPU OS 16_0) Safari/604.1"
        result = UserAgentParser.parse(ua)
        self.assertEqual(result['device_type'], 'tablet')

    def test_parse_empty_string(self):
        """Test empty user agent."""
        result = UserAgentParser.parse("")
        self.assertEqual(result['device_type'], 'unknown')
        self.assertEqual(result['browser'], 'unknown')
        self.assertEqual(result['os'], 'unknown')

    def test_parse_caching(self):
        """Test that parsing is cached."""
        ua = "Mozilla/5.0 (Windows NT 10.0) Chrome/120.0"
        result1 = UserAgentParser.parse(ua)
        result2 = UserAgentParser.parse(ua)
        # Should return same cached dict
        self.assertIs(result1, result2)


class EnhancedTrackingServiceTests(TestCase):
    """Tests for EnhancedTrackingService class."""

    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='testuser',
            password=TEST_USER_PASSWORD
        )
        self.factory = RequestFactory()

    def test_is_tracking_enabled_default_false(self):
        """Test tracking is disabled by default."""
        result = EnhancedTrackingService.is_tracking_enabled('nonexistent')
        self.assertFalse(result)

    def test_get_tracking_statistics(self):
        """Test statistics retrieval."""
        stats = EnhancedTrackingService.get_tracking_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('file_operations_24h', stats)
        self.assertIn('user_actions_24h', stats)

    def test_suspicious_request_detection(self):
        """Test suspicious request detection."""
        request = self.factory.get('/api/test', {'q': "'; DROP TABLE users; --"})
        suspicion = InputValidator.is_suspicious_request(request)
        self.assertTrue(suspicion['sql_injection'])

    def test_xss_request_detection(self):
        """Test XSS request detection."""
        request = self.factory.get('/api/test', {'name': "<script>alert('x')</script>"})
        suspicion = InputValidator.is_suspicious_request(request)
        self.assertTrue(suspicion['xss_attempt'])

    def test_path_traversal_detection(self):
        """Test path traversal detection."""
        request = self.factory.get('/../../etc/passwd')
        suspicion = InputValidator.is_suspicious_request(request)
        self.assertTrue(suspicion['path_traversal'])
