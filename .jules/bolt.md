## 2026-02-05 - Optimized Vendor Analytics & Fixed Test Environment
**Learning:** `django-csp` 4.0+ requires dictionary-based `CONTENT_SECURITY_POLICY` configuration. `django-celery-beat` requires `Django<6.0`. Testing API views with `APIClient` requires `permission_classes=[AllowAny]` if `DEFAULT_PERMISSION_CLASSES` is `IsAuthenticated`. Middleware order matters for `request.session` access.
**Action:** Always check `settings.py` middleware order and library versions when encountering environment or permission issues in tests. Use database aggregation for analytics instead of Python loops.
