
from django.test import SimpleTestCase
from django.http import HttpRequest
from store.tracking_service import InputValidator

class SecurityTrackingTest(SimpleTestCase):
    def test_email_false_positive(self):
        """Test that valid emails are NOT flagged as SQL injection."""
        email = "test@example.com"

        # Test direct detection
        self.assertFalse(InputValidator.detect_sql_injection(email), "Should NOT flag valid email")

        # Test request checking
        request = HttpRequest()
        request.POST = {'email': email}
        suspicion = InputValidator.is_suspicious_request(request)
        self.assertFalse(suspicion['sql_injection'], "Should NOT flag request with email")

    def test_actual_sql_injection(self):
        """Test that actual SQL injection is still detected."""
        # Only testing patterns that are explicitly covered by the regex
        payloads = [
            "UNION SELECT * FROM users",
            "DROP TABLE users",
            "@@version",
            "admin'; --"
        ]
        for payload in payloads:
            self.assertTrue(InputValidator.detect_sql_injection(payload), f"Should detect: {payload}")
