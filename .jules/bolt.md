## 2024-05-22 - Django Settings & Redis Coupling
**Learning:** `config/settings.py` unconditionally configures Redis as the cache backend if `django-redis` is installed, without checking an environment variable (like `NO_REDIS`). This makes running tests in environments without Redis difficult, as `pytest-django` loads these settings.
**Action:** When running tests in CI/sandbox without Redis, use a `test_settings.py` that overrides `CACHES` to `LocMemCache` and `SESSION_ENGINE` to `db` or `cache` (with local mem), or mock `is_package_installed`.
