## 2024-05-22 - N+1 Queries in SerializerMethodField
**Learning:** `SerializerMethodField` often causes N+1 queries when accessing related objects (like `obj.reviews.count()`) or performing per-item checks (like `Wishlist.objects.filter(product=obj)`). These are not solved by `select_related` alone.
**Action:** Use `queryset.annotate()` for aggregates (Count, Avg) and `prefetch_related()` for related lists. For user-specific state (like wishlist), fetch all relevant IDs in the view and pass them via `serializer_context` to perform O(1) lookups in the serializer.
