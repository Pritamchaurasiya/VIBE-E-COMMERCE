## 2024-05-23 - Race Condition in Coupon Service
**Vulnerability:** A race condition existed in `store/coupon_service.py` where `used_count` was incremented using Python arithmetic (`coupon.used_count += 1`) followed by `save()`. This could allow concurrent requests to exceed the coupon's usage limit.
**Learning:** High-concurrency environments require database-level atomicity for counters. Django's `F()` expressions or `filter().update()` should be used.
**Prevention:** Always use `F()` expressions for incrementing/decrementing counters in models, or use `filter(condition).update()` to atomically check conditions and update in a single query.
