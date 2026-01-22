## 2025-02-19 - Environment & Configuration Gotchas

**Learning:** `django-redis` configuration in `settings.py` was unconditionally enabled if the package was installed, breaking tests in environments without Redis (like CI or local test runs).
**Action:** Always wrap `django-redis` configuration with a check for `NO_REDIS` environment variable to ensure tests can run with `LocMemCache`.

**Learning:** `django-csp` version 4.0+ deprecates tuple-based configuration in favor of dictionary-based `CONTENT_SECURITY_POLICY`.
**Action:** When upgrading `django-csp`, ensure `settings.py` is updated to use the new dictionary format for directives.

**Learning:** `requirements.txt` contained conflicting Django versions (`>=6.0` vs dependency constraints requiring `<6.0`), causing installation failures.
**Action:** Always verify `requirements.txt` for version conflicts, especially when multiple packages have strict Django version dependencies.
