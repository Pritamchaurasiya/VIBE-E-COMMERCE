## 2025-02-18 - Coupon Race Condition & Strict Auth Defaults
**Vulnerability:** A race condition in `Coupon.apply_coupon` allowed users to bypass `max_uses` limits by sending concurrent requests.
**Learning:** Django's `update()` with `F()` expressions is essential for atomic updates on counters. Also, this codebase enforces `IsAuthenticated` by default in `settings.py`, which caused regressions in public API endpoints when tests were run, requiring explicit `permission_classes = [AllowAny]` on public views.
**Prevention:** Always use atomic updates for quota/limit enforcement. Explicitly define permissions on all views to avoid implicit defaults breaking functionality.
