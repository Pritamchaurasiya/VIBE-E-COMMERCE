## 2025-02-18 - Performance & Testing Learnings
**Learning:** `django-redis` forces Redis backend if installed, breaking tests in environments without Redis.
**Action:** Exclude `django_redis` configuration or override `CACHES` setting when `TESTING` env var is set.

**Learning:** `axes` middleware and backend can block test clients or cause errors.
**Action:** Exclude `axes` from `INSTALLED_APPS`, `MIDDLEWARE`, and `AUTHENTICATION_BACKENDS` when `TESTING` is True.

**Learning:** `Profile` model has a `post_save` signal creating instances, causing `IntegrityError` in `RegisterView`.
**Action:** Use `get_or_create` in views that create users with profiles.
