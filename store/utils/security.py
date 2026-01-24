"""
Security utilities for the store application.

Provides helper functions for input validation, sanitization, and security checks.
"""
import re
import html
import hashlib
import secrets
from functools import wraps
from typing import Optional

from django.core.cache import cache
from django.http import JsonResponse


# ============================================================================
# INPUT VALIDATION
# ============================================================================

EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

PHONE_REGEX = re.compile(
    r'^[+]?\d{10,15}$'
)

GST_REGEX = re.compile(
    r'^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[\dA-Z]$'
)

PAN_REGEX = re.compile(
    r'^[A-Z]{5}\d{4}[A-Z]$'
)


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    if not email or len(email) > 254:
        return False
    return bool(EMAIL_REGEX.match(email))


def is_valid_phone(phone: str) -> bool:
    """Validate phone number format."""
    if not phone:
        return False
    # Remove spaces and dashes
    cleaned = phone.replace(' ', '').replace('-', '')
    return bool(PHONE_REGEX.match(cleaned))


def is_valid_gst(gst: str) -> bool:
    """Validate GST number format (Indian)."""
    if not gst:
        return False
    return bool(GST_REGEX.match(gst.upper()))


def is_valid_pan(pan: str) -> bool:
    """Validate PAN number format (Indian)."""
    if not pan:
        return False
    return bool(PAN_REGEX.match(pan.upper()))


# ============================================================================
# INPUT SANITIZATION
# ============================================================================

def sanitize_html(text: str) -> str:
    """Escape HTML characters to prevent XSS."""
    if not text:
        return ""
    return html.escape(str(text))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    if not filename:
        return ""
    # Remove path components
    filename = filename.replace('\\', '/').split('/')[-1]
    # Remove potentially dangerous characters
    dangerous_chars = ['..', '<', '>', ':', '"', '|', '?', '*', '\0']
    for char in dangerous_chars:
        filename = filename.replace(char, '')
    # Limit length
    return filename[:255]


def sanitize_search_query(query: str) -> str:
    """Sanitize search query to prevent injection."""
    if not query:
        return ""
    # Remove SQL-like keywords
    dangerous_patterns = [
        r'\b(union|select|insert|update|delete|drop|exec|execute)\b',
        r'[;\'\"--]'
    ]
    result = query
    for pattern in dangerous_patterns:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    return result.strip()[:200]


def sanitize_for_csv(value):
    """
    Sanitize a value for CSV export to prevent formula injection.

    If the value starts with any of the formula trigger characters (=, +, -, @),
    prepend a single quote to force it to be treated as a string.
    """
    if value is None:
        return ""

    value_str = str(value)
    if value_str and value_str[0] in ('=', '+', '-', '@'):
        return "'" + value_str

    return value_str


# ============================================================================
# RATE LIMITING
# ============================================================================

def rate_limit(key_prefix: str, max_attempts: int = 5, period: int = 60):
    """
    Decorator for rate limiting API endpoints.

    Args:
        key_prefix: Unique identifier for the rate limit
        max_attempts: Maximum attempts allowed in the period
        period: Time period in seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Get client identifier
            client_ip = get_client_ip(request)
            rate_key = f"rate_limit:{key_prefix}:{client_ip}"

            # Get current count
            attempts = cache.get(rate_key, 0)

            if attempts >= max_attempts:
                return JsonResponse({
                    'error': 'Too many requests',
                    'message': 'Please wait before trying again.',
                    'retry_after': period
                }, status=429)

            # Increment counter
            cache.set(rate_key, attempts + 1, period)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_client_ip(request) -> str:
    """Extract client IP from request, handling proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip
    return request.META.get('REMOTE_ADDR', 'unknown')


# ============================================================================
# TOKEN GENERATION
# ============================================================================

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code."""
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


def hash_sensitive_data(data: str, salt: Optional[str] = None) -> str:
    """Hash sensitive data for secure storage/comparison."""
    if salt is None:
        salt = secrets.token_hex(16)
    combined = f"{salt}:{data}"
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_hashed_data(data: str, hashed_value: str) -> bool:
    """Verify data against its hash."""
    try:
        salt = hashed_value.split(':')[0]
        return hash_sensitive_data(data, salt) == hashed_value
    except (ValueError, IndexError):
        return False


# ============================================================================
# SENSITIVE DATA MASKING
# ============================================================================

def mask_email(email: str) -> str:
    """Mask email for display (e.g., j***n@example.com)."""
    if not email or '@' not in email:
        return email
    local, domain = email.rsplit('@', 1)
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask phone for display (e.g., +91 ****1234)."""
    if not phone or len(phone) < 4:
        return phone
    return '*' * (len(phone) - 4) + phone[-4:]


def mask_card_number(card: str) -> str:
    """Mask card number (e.g., **** **** **** 1234)."""
    if not card or len(card) < 4:
        return card
    return '**** **** **** ' + card[-4:]


# ============================================================================
# CONTENT SECURITY
# ============================================================================

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB


def is_safe_file_upload(file, allowed_extensions: set, max_size: int) -> tuple:
    """
    Validate file upload for security.

    Returns:
        tuple: (is_safe, error_message)
    """
    if not file:
        return False, "No file provided"

    # Check size
    if file.size > max_size:
        return False, f"File too large. Maximum size is {max_size // (1024*1024)}MB"

    # Check extension
    ext = file.name.split('.')[-1].lower() if '.' in file.name else ''
    if ext not in allowed_extensions:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"

    # For images, verify magic bytes
    if allowed_extensions <= ALLOWED_IMAGE_EXTENSIONS:
        file.seek(0)
        header = file.read(8)
        file.seek(0)

        # Check magic bytes for common image formats
        magic_signatures = {
            b'\xff\xd8\xff': 'jpeg',
            b'\x89PNG': 'png',
            b'GIF87a': 'gif',
            b'GIF89a': 'gif',
            b'RIFF': 'webp',
        }

        is_valid_image = any(header.startswith(sig) for sig in magic_signatures)
        if not is_valid_image:
            return False, "Invalid image file content"

    return True, None


# ============================================================================
# PASSWORD STRENGTH
# ============================================================================

def check_password_strength(password: str) -> tuple:
    """
    Check password strength.

    Returns:
        tuple: (is_strong, list of issues)
    """
    issues = []

    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")

    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")

    # Check for common weak passwords
    weak_passwords = [
        'password', '123456', '12345678', 'qwerty', 'abc123',
        'password1', 'admin', 'letmein', 'welcome'
    ]
    if password.lower() in weak_passwords:
        issues.append("Password is too common")

    return len(issues) == 0, issues
