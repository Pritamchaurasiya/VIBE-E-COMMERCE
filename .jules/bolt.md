## 2025-05-22 - [Optimized Product List and Fixed Test Environment]
**Learning:** `django-redis` installation forces Redis usage in `settings.py` unless explicitly checked against `NO_REDIS` env var. Also, `AnonRateThrottle` can block tests if not disabled. `IntegrityError` in `RegisterView` was due to signals creating related objects.
**Action:** Always verify `settings.py` logic for environment variable overrides. Use `get_or_create` when signals are involved in object creation. Disable throttling in test environments.
