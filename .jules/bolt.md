## 2024-05-22 - DRF Serializer Method Fields & N+1 Queries
**Learning:** DRF's `SerializerMethodField` is a hidden performance killer. `ProductSerializer` was making 3 separate DB queries (wishlist, rating, review count) for *every* item in the list. Even with `select_related` in the View, the Serializer methods run for each instance.
**Action:**
1. Use `annotate()` in the View's `get_queryset` to calculate aggregates (Count, Avg) in the main query.
2. Update Serializer to check for these annotated attributes (e.g., `hasattr(obj, 'annotated_field')`) before falling back to the DB method.
3. For user-specific data (like Wishlist), fetch all relevant IDs in `get_serializer_context` and pass a set/dict for O(1) lookups.
4. Always add `.prefetch_related()` for reverse relationships (like `images`) if the serializer accesses them.
