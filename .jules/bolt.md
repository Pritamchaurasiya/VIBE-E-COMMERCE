## 2025-05-28 - Optimized Product List & Fixed Configs
**Learning:** `django-redis` connection errors in tests require overriding `CACHES` setting to use `LocMemCache`. `SecurityTrackingMiddleware` needs to respect `PYTEST_CURRENT_TEST` env var to avoid blocking tests. `django-csp` 4.0 requires dictionary-based configuration.
**Action:** Always check `settings.py` and middleware when tests fail with 401/403 or connection errors. Ensure `requirements.txt` dependencies are compatible.
