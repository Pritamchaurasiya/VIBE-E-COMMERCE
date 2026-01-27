## 2024-05-23 - Django Middleware & Tracking System Fragility
**Learning:** `SecurityTrackingMiddleware` was placed before `SessionMiddleware` in `settings.py`, causing `WSGIRequest object has no attribute 'session'` errors because session wasn't initialized yet. Middleware order is critical and silent failures in middleware can manifest as 403s or 500s in specific views.
**Action:** Always verify middleware dependencies (like Session) are placed *before* dependent middleware (like Security/Tracking) in `MIDDLEWARE` list.

## 2024-05-23 - Circular Imports in Service Layer
**Learning:** `store/tracking_service.py` attempted to lazy import `tracking_models` using `from . import tracking_models`, but `store/__init__.py` did not expose it. This caused `ImportError` in tests.
**Action:** Use direct imports (e.g., `from . import models as tracking_models`) or ensure `__init__.py` exposes expected modules if using package-level imports.

## 2024-05-23 - Default Permissions Regression
**Learning:** `REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = ['IsAuthenticated']` caused public views (Products, Categories) to reject anonymous users because they lacked explicit `permission_classes = [AllowAny]`.
**Action:** Explicitly define `permission_classes` on all public API views to avoid relying on defaults that might be too restrictive.
