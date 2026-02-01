## 2024-05-23 - Vendor Analytics O(N) Optimization
**Learning:** `VendorAnalyticsAPIView` was iterating over all `OrderItem` objects in Python to calculate total revenue, monthly revenue, and weekly revenue. This is an O(N) operation where N is the number of order items, which can be very slow for vendors with many orders.
**Action:** Replaced the Python iteration with database-level aggregation using Django's `Sum`, `Case`, and `When`. This offloads the calculation to the database (O(1) from Python's perspective, efficient O(N) in DB) and avoids loading thousands of model instances into memory.

## 2024-05-23 - Django CSP Configuration
**Learning:** `django-csp` 4.0+ enforces a dictionary-based configuration for `CONTENT_SECURITY_POLICY`. Legacy flat settings cause `SystemCheckError`.
**Action:** Updated `config/settings.py` to use the new `CONTENT_SECURITY_POLICY` dictionary format.

## 2024-05-23 - Testing Environment & Redis
**Learning:** `django-redis` is configured in `settings.py` if installed, but tests running with `sqlite` (no Redis service) fail unless explicitly disabled.
**Action:** Modified `config/settings.py` to check for `TESTING` environment variable and fall back to `LocMemCache` during tests.
