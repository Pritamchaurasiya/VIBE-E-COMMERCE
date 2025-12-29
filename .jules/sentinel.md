## 2025-02-18 - Parameter Tampering in Financial Logic
**Vulnerability:** Client-side manipulation of 'cart_total' parameter in coupon and deal application endpoints.
**Learning:** Both standard Django views and DRF API views relied on user-submitted data for critical financial calculations (minimum order value checks, discount calculations) instead of recalculating the cart total on the server.
**Prevention:** Always recalculate financial totals on the server side using the session/database state (e.g., `Cart(request).get_total_cost()`) and never trust client-provided values for pricing logic.
