## 2025-02-18 - Django Settings & Environment Dependencies
**Learning:** The project relies on `django-redis` for caching and throttling, which causes `ConnectionError` in environments without a running Redis instance. Tests must override `CACHES` and `SESSION_ENGINE` to use `LocMemCache` and `db` backend respectively, and disable throttling classes if they rely on the cache.
**Action:** When running tests in CI or isolated environments, always ensure `override_settings` is used to decouple from external services like Redis.

## 2025-02-18 - Legacy CSP Configuration
**Learning:** `django-csp` version 4.0+ requires `CONTENT_SECURITY_POLICY` to be a dictionary with `DIRECTIVES`, replacing the old tuple-based configuration (e.g., `CSP_DEFAULT_SRC`). Failure to update this causes `SystemCheckError` preventing startup.
**Action:** Check for legacy CSP configurations when upgrading Django packages or encountering startup errors related to security settings.
