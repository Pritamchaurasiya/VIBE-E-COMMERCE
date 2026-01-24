from django.test import TestCase, RequestFactory
from store.tracking_service import InputValidator

class SQLInjectionFixTests(TestCase):
    """Tests for the SQL injection false positive fix."""

    def test_email_address_is_not_sql_injection(self):
        """Test that a valid email address is NOT flagged as SQL injection."""
        email = "user@example.com"
        self.assertFalse(
            InputValidator.detect_sql_injection(email),
            f"Email '{email}' should not be flagged as SQL injection"
        )

    def test_complex_email_address_is_not_sql_injection(self):
        """Test that a complex email address is NOT flagged as SQL injection."""
        email = "firstname.lastname+category@domain.co.uk"
        self.assertFalse(
            InputValidator.detect_sql_injection(email),
            f"Email '{email}' should not be flagged as SQL injection"
        )

    def test_actual_sql_injection_is_flagged(self):
        """Test that actual SQL injection patterns are still flagged."""
        patterns = [
            "'; DROP TABLE users; --",
            "SELECT * FROM users",
            "UNION SELECT password",
            "admin' --",
            "@@version",
            "WAITFOR DELAY '0:0:5'"
        ]
        for pattern in patterns:
            self.assertTrue(
                InputValidator.detect_sql_injection(pattern),
                f"Pattern '{pattern}' should be flagged as SQL injection"
            )

    def test_suspicious_request_with_email(self):
        """Test that a request with an email in POST data is not suspicious."""
        factory = RequestFactory()
        request = factory.post('/login', {'email': 'user@example.com', 'password': 'password123'})

        suspicion = InputValidator.is_suspicious_request(request)
        self.assertFalse(
            suspicion['sql_injection'],
            "Request with email should not be suspicious"
        )
