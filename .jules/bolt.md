## 2024-05-24 - Optimized Vendor Dashboard Counts
**Learning:** Combining multiple `count()` queries into a single `aggregate` call with conditional `Count` significantly reduces database round-trips.
**Action:** When seeing multiple counts on the same queryset with different filters, always refactor to use aggregation.
