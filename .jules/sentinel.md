## 2024-05-23 - Client-Side Trust in Financial Calculations
**Vulnerability:** The `apply_coupon` and `apply_deal` endpoints (both in standard views and API views) trusted the `cart_total` sent by the client to calculate discounts and validate minimum order requirements.
**Learning:** Developers often pass totals from the frontend for convenience, but financial calculations must always be re-verified on the server side using the source of truth (database/session).
**Prevention:** Always recalculate order totals on the server using `Cart` or database lookups before applying any discounts or processing payments. Never trust `request.data['amount']` or similar fields for critical logic.
