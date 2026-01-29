## 2024-05-24 - Vendor Analytics Optimization
**Learning:** The `VendorAnalyticsAPIView` was fetching all order items into memory to calculate revenue using Python loops. This works for small datasets but scales poorly (O(n) memory and time).
**Action:** Replaced with DB-side aggregation using `Sum` and conditional `Case`/`When`. This reduces memory usage to O(1) and leverages the DB's efficiency. Also combined multiple `count()` queries into a single `aggregate()` call using `filter` (Django 2.0+ feature).
**Environment:** Tests required explicitly overriding `CACHES` to `LocMemCache` and disabling throttling to avoid Redis connection errors in the CI/Sandbox environment.
