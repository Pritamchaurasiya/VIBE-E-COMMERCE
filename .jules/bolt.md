## 2026-01-14 - [Backend] Django Serializer N+1 Pitfall with Nested Prefetches

**Learning:** Prefetching nested relationships (`prefetch_related('items__product')`) does *not* automatically solve N+1 issues if the serializer uses `SerializerMethodField` or properties to access related objects (like `reviews` or `wishlist`) that are not part of the initial prefetch. Furthermore, Django's `prefetch_related` cannot easily "inject" aggregated annotations (like `Avg('rating')`) into the prefetched objects without complex query construction.

**Action:**
1.  **Serializer Intelligence:** Modify serializers to check for annotated attributes (e.g., `hasattr(obj, 'avg_rating')`) or prefetched caches (e.g., `'reviews' in obj._prefetched_objects_cache`) before hitting the database.
2.  **Explicit Prefetching:** In the View, use `Prefetch` objects to explicitly load these related sets (e.g., `Prefetch('items__product__images')`) and inject them into the serializer's accessible context.
3.  **Optimization:** For `OrderListView`, I reduced queries by ~50% (56 -> 28) by prefetching images and using a user-filtered prefetch for the `wishlist` status check, avoiding 1-2 extra queries *per item*.
