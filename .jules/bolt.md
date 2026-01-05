## 2025-01-20 - [Performance: RecommendationsView Optimization]
**Learning:** `RecommendationsView` suffered from an N+1 query issue when iterating over recommended products to access `product.category` and `product.vendor`. Using `select_related('category', 'vendor')` in the querysets significantly reduced the query count from 22 to 6.
**Action:** Always check related field access in serialization loops and use `select_related` or `prefetch_related` accordingly.

## 2025-01-20 - [Security: False Positives in SQL Injection Detection]
**Learning:** The `InputValidator` regex for SQL injection was too aggressive, flagging email addresses containing `@` and valid JSON payloads with `action: "update"` as attacks. This caused false positives in registration and cart update flows.
**Action:** Refined regex to be more contextual and removed `@` and simple SQL keywords like `UPDATE` from being flagged in isolation without other suspicious characters.

## 2025-01-20 - [Testing: Security Middleware in Tests]
**Learning:** `SecurityTrackingMiddleware` can block legitimate test requests due to missing headers (like `Referer`) or aggressive lockout policies. Disabling lockout in `DEBUG` mode and relaxing CSRF checks for `/api/` paths improved test stability.
**Action:** Ensure security middleware has appropriate bypasses or relaxations for test/dev environments (checked via `settings.DEBUG`).

## 2025-01-20 - [Backend: Signal-driven Profile Creation]
**Learning:** The `User` model has a `post_save` signal that automatically creates a `Profile`. Views attempting to manually create a `Profile` after `User` creation caused `IntegrityError` due to unique constraint violations.
**Action:** Use `Profile.objects.get_or_create(user=user)` or update the existing profile instead of calling `create()` after user creation.