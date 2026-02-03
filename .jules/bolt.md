## 2025-05-20 - Django Dependency and Settings Conflicts
**Learning:** `django-csp` 4.0+ requires a dictionary-based `CONTENT_SECURITY_POLICY` configuration and raises a `SystemCheckError` if legacy tuple settings are used. Also, `django-celery-beat` may not yet support `Django>=6.0`, causing dependency resolution failures.
**Action:** When upgrading dependencies, always verify configuration format changes in `settings.py` and check compatibility matrices for major framework upgrades.

## 2025-05-20 - Test Environment Isolation
**Learning:** `django-redis` attempts to connect to Redis during tests unless explicitly disabled or mocked. `override_settings` with `LocMemCache` is essential for view/integration tests.
**Action:** Ensure all view tests using cache/session include `@override_settings(CACHES=..., SESSION_ENGINE=...)`.
