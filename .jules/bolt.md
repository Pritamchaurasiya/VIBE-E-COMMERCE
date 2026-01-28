## 2024-05-23 - Dashboard Stats Optimization
**Learning:** `DashboardStatsView` was performing ~24 separate database queries to gather metrics. Using `aggregate` with conditional `Count` and `Sum` (via `filter=Q(...)`) reduced this to 2 main queries (10 total queries including side-stats), a >50% reduction.
**Action:** Prefer `aggregate` with `filter` over multiple `filter().count()` or `filter().aggregate()` calls when calculating multiple metrics from the same queryset.

## 2024-05-23 - Vendor Product Count Bug
**Learning:** `Vendor` model uses `related_name='products'` for the `Product` relationship. Using `Count('product')` in annotations raises a `FieldError`.
**Action:** Always verify `related_name` in models before using reverse relationships in queries. Use `Count('products')` for Vendor-Product relationship.
