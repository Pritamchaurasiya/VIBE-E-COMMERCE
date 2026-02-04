## 2025-02-23 - Testing Environment Challenges
**Learning:** The Django test suite relies on a running Redis instance and Postgres by default, causing connection errors in CI/test environments without them. Also, `ProductListView` had incorrect permissions blocking access.
**Action:** Use `@override_settings` to mock cache/session in tests. Explicitly set `permission_classes` for public views.
