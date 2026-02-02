## 2025-02-02 - Testing Environment & Permissions
**Learning:** `django-redis` configuration in `settings.py` was unconditionally enabled if installed, causing tests to fail in environments without Redis (like CI).
**Action:** Always check `TESTING` environment variable or similar flag before configuring external services like Redis in `settings.py`.

**Learning:** Public views like `ProductListView` were inheriting `IsAuthenticated` from `DEFAULT_PERMISSION_CLASSES` because they lacked explicit `permission_classes`.
**Action:** Explicitly set `permission_classes = [permissions.AllowAny]` for views intended to be public, even if tests seem to pass (they might be mocking auth or running in a different config).
