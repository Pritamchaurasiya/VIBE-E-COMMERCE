## 2026-01-16 - [Optimized Admin Dashboard]
**Learning:** Combining multiple Django aggregations (`Count`, `Sum`) into a single query using `filter=Q(...)` significantly reduces database roundtrips for dashboard views. Also, `Count(distinct=True)` is crucial when counting main entities in a query involving joins (e.g. `Vendor` joined with `Product`).
**Action:** Look for similar patterns in other analytics views where multiple `filter(...).count()` or `aggregate(...)` calls are made on the same queryset.
