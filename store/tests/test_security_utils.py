from django.test import TestCase
from store.tracking_service import InputValidator

class SecurityUtilsTest(TestCase):
    def test_sql_injection_false_positive_email(self):
        """Test that valid email addresses do not trigger SQL injection detection."""
        # This currently returns True (fail)
        self.assertFalse(InputValidator.detect_sql_injection("user@example.com"))
        self.assertFalse(InputValidator.detect_sql_injection("firstname.lastname@company.co.uk"))

    def test_sql_injection_detection(self):
        """Test that actual SQL injection patterns are detected."""
        self.assertTrue(InputValidator.detect_sql_injection("SELECT * FROM users"))
        self.assertTrue(InputValidator.detect_sql_injection("UNION SELECT"))
        self.assertTrue(InputValidator.detect_sql_injection("@@VERSION"))
        self.assertTrue(InputValidator.detect_sql_injection("1; DROP TABLE users"))
