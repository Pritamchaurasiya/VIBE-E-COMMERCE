# Sentinel's Journal

## 2025-02-09 - Financial Logic Bypassed via Client-Side Input
**Vulnerability:** IDOR / Logic Bypass in `ApplyCouponView`. The view accepted `cart_total` from the client-side `request.data`, allowing users to manipulate the total amount used for coupon validation (minimum order value) and discount calculation.
**Learning:** Never trust client-side input for critical financial calculations or validation logic. Even if the client app sends it innocently, an attacker can modify it.
**Prevention:** Always recalculate values like cart totals, prices, and permissions on the server-side using trusted data sources (database, session, etc.). Use `Cart(request).get_total_cost()` instead of `request.data.get('total')`.
