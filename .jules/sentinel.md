## 2024-05-23 - Race Condition in Coupon Service
**Vulnerability:** A race condition in `apply_coupon` allowed users to bypass coupon usage limits by sending concurrent requests. The method blindly incremented `used_count` and saved it, leading to lost updates and over-usage.
**Learning:** High-concurrency environments require atomic database operations for shared resources like counters. Simple read-modify-write patterns are unsafe.
**Prevention:** Use Django's `F()` expressions and `update()` method to perform atomic updates directly at the database level. Combine with filters to enforce invariants (like `used_count < max_uses`) in the same atomic operation.
