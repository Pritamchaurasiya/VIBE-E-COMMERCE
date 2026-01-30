## 2024-05-23 - Product List Optimization
**Learning:** `ProductSerializer` accessed related fields (`images`, `reviews`) via methods without prefetching in `ProductListView`, causing N+1 queries (101 queries for 20 items). `obj.reviews.all()` inside a serializer method triggers a query if not prefetched, and `aggregate` triggers another.
**Action:** Use `prefetch_related` for images and `annotate` for aggregated values (`Avg`, `Count`) and `Exists` for boolean checks in the `get_queryset` method. Update serializer to use these annotated attributes if available. Reduced queries to 2.
