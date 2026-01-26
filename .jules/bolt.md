## 2025-02-18 - Test Environment Redis Dependency
**Learning:** Backend tests failed to run because `config/settings.py` configures Redis cache if `django-redis` is installed, ignoring the `NO_REDIS` environment variable if not explicitly checked (which it wasn't). Tests require overriding settings to use `LocMemCache` explicitly.
**Action:** When writing backend tests involving cache, use `@override_settings(CACHES=..., SESSION_ENGINE='django.contrib.sessions.backends.db')` to ensure independence from external services like Redis.
