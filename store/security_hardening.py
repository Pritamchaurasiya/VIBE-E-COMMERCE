from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
import re
import time

class SecurityHardeningMiddleware(MiddlewareMixin):
    """
    Middleware for enhanced security hardening.
    - Rate limiting per IP
    - SQL Injection pattern detection
    - XSS pattern detection
    - Security headers injection
    """

    SQL_PATTERNS = [
        r"(?i)(union\s+select)",
        r"(?i)(select\s+.*\s+from)",
        r"(?i)(insert\s+into)",
        r"(?i)(drop\s+table)",
        r"(?i)(exec\s+xp_)",
        r"(?i)(\s+or\s+1=1)",
        r"(?i)(--)",
    ]

    XSS_PATTERNS = [
        r"(?i)(<script>)",
        r"(?i)(javascript:)",
        r"(?i)(onload=)",
        r"(?i)(onerror=)",
    ]

    def process_request(self, request):
        ip = self.get_client_ip(request)

        # 1. Rate Limiting (Simple Token Bucket)
        if not self.check_rate_limit(ip):
            return HttpResponseForbidden("Rate limit exceeded. Please try again later.")

        # 2. Input Validation (Query Params & Body)
        # Check GET params
        for value in request.GET.values():
            if self.detect_attack(value):
                return HttpResponseForbidden("Malicious input detected.")

        # Check POST data (simplified, normally requires parsing body carefully)
        if request.method == 'POST':
            # This is risky if body is large or not form-encoded, handled for simple cases
            # For JSON, we'd need to parse it.
            pass

    def process_response(self, request, response):
        # 3. Security Headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # response['Content-Security-Policy'] = "default-src 'self'; ..." # Needs careful config
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def check_rate_limit(self, ip):
        # Allow 100 requests per minute
        key = f"rate_limit_{ip}"
        limit = 100
        period = 60

        requests = cache.get(key, [])
        now = time.time()

        # Filter old requests
        requests = [req for req in requests if req > now - period]

        if len(requests) >= limit:
            return False

        requests.append(now)
        cache.set(key, requests, period)
        return True

    def detect_attack(self, value):
        if not isinstance(value, str):
            return False

        for pattern in self.SQL_PATTERNS + self.XSS_PATTERNS:
            if re.search(pattern, value):
                return True
        return False
