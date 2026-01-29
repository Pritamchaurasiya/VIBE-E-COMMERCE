## 2025-02-19 - Dashboard Optimization
**Learning:** `DashboardStatsView` was making sequential database queries for each metric (total revenue, monthly revenue, etc.), resulting in N+1 style behavior at the view level (24 queries).
**Action:** Replaced sequential queries with Django's `aggregate` combined with `filter=Q(...)` (conditional aggregation). This allows fetching multiple metrics in a single database round-trip. Reduced query count from 24 to 7. Also fixed a `FieldError` where `Count('product')` was used instead of `Count('products')` for the Vendor model.
