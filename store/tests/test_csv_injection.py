
import csv
import io
from decimal import Decimal
import pytest
from store.utils import sanitize_csv_field

def test_sanitize_csv_field_escape():
    """Test that fields starting with dangerous chars are escaped."""
    assert sanitize_csv_field("=cmd") == "'=cmd"
    assert sanitize_csv_field("+cmd") == "'+cmd"
    assert sanitize_csv_field("-cmd") == "'-cmd"
    assert sanitize_csv_field("@cmd") == "'@cmd"

def test_sanitize_csv_field_safe():
    """Test that safe fields are not modified."""
    assert sanitize_csv_field("safe") == "safe"
    assert sanitize_csv_field("123") == "123"
    assert sanitize_csv_field("") == ""
    assert sanitize_csv_field(None) == ""

def test_sanitize_csv_field_numeric():
    """Test that numeric types are preserved without escaping if safe."""
    # Integers
    assert sanitize_csv_field(123) == "123"
    assert sanitize_csv_field(-123) == "-123"  # Should this be escaped? -123 is a formula? No, usually treated as number.
    # Excel treats "-123" as a number. But "-1+1" as formula.
    # Our sanitizer escapes anything starting with -.
    # If we refine it to allow pure numbers, that's better.

    # Decimals
    assert sanitize_csv_field(Decimal("12.34")) == "12.34"
    assert sanitize_csv_field(Decimal("-12.34")) == "-12.34"

def test_sanitize_csv_field_formula_like_string():
    """Test string that looks like formula."""
    assert sanitize_csv_field("=1+1") == "'=1+1"
    assert sanitize_csv_field("-1+1") == "'-1+1"

def test_csv_writer_integration():
    """Test integration with csv writer."""
    output = io.StringIO()
    writer = csv.writer(output)

    malicious = "=cmd|' /C calc'!A0"
    safe = "John Doe"

    writer.writerow([sanitize_csv_field(malicious), sanitize_csv_field(safe)])

    content = output.getvalue().strip()

    assert "'=cmd" in content or "\"'=cmd" in content
