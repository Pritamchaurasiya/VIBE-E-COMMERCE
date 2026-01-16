## 2025-05-15 - [Race Condition in Coupon Application]
**Vulnerability:** A race condition in `store/coupon_service.py` allowed users to apply the same coupon multiple times concurrently, exceeding the `max_uses` limit.
**Learning:** Checking a condition and then updating a value in separate steps is not thread-safe. Django `F()` expressions and atomic updates (`update()`) are essential for concurrent correctness.
**Prevention:** Always use atomic updates (`queryset.update()`) with condition filtering (`filter(count__lt=max)`) for decrementing stock or incrementing usage counters.
