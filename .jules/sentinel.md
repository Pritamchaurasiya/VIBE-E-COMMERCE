## 2024-05-22 - Race Condition in Coupon Redemption
**Vulnerability:** Race condition in `store/coupon_service.py` allowing coupons to be redeemed beyond their `max_uses` limit.
**Learning:** High-concurrency environments can bypass simple "read-then-write" logic. Django ORM `get()` followed by increment and `save()` is not atomic.
**Prevention:** Use `F()` expressions for atomic updates combined with filters (e.g., `filter(used_count__lt=F('max_uses')).update(...)`) to enforce invariants at the database level.
