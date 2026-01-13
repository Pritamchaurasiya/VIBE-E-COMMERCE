
import pytest
from store.utils.security import sanitize_csv_field

class TestCSVSecurity:
    """Test CSV injection protection."""

    @pytest.mark.parametrize("input_val,expected", [
        ("Normal Text", "Normal Text"),
        ("=SUM(1+1)", "'=SUM(1+1)"),
        ("+12345", "'+12345"),
        ("-100", "'-100"),
        ("@username", "'@username"),
        ("%something", "'%something"),
        ("| pipe", "'| pipe"),
        ("Safe=Text", "Safe=Text"),
        (None, ""),
        (123, "123"),
    ])
    def test_sanitize_csv_field(self, input_val, expected):
        """Test that dangerous characters are escaped."""
        assert sanitize_csv_field(input_val) == expected

    def test_sanitize_csv_field_type_handling(self):
        """Test that different types are handled correctly."""
        assert sanitize_csv_field(123) == "123"
        assert sanitize_csv_field(12.34) == "12.34"
        assert sanitize_csv_field(True) == "True"
