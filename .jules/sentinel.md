## 2024-05-24 - Race Condition in Coupon Service
**Vulnerability:** A classic Read-Modify-Write race condition was identified in `CouponService.apply_coupon`, where `coupon.used_count` was incremented and saved non-atomically.
**Learning:** High-concurrency environments (like flash sales) can exploit non-atomic updates to bypass limits (e.g., `max_uses`), leading to financial loss.
**Prevention:** Always use atomic database operations (`F()` expressions) combined with conditional filtering (`filter(count__lt=limit).update(count=F('count')+1)`) when enforcing strict limits on counters.
