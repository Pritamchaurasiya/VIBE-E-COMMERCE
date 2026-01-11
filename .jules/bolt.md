## 2026-01-11 - N+1 Queries in Django DRF
**Learning:** In Django Rest Framework, standard `SerializerMethodField` usage for related objects (like `images`, `reviews`, or `wishlist` checks) often causes N+1 query problems because DRF iterates over objects and calls the method for each one.
**Action:** Always optimize by:
1. Using `prefetch_related` or `select_related` in the View's queryset.
2. Annotating calculated fields (e.g., `avg_rating`, `review_count`) in the queryset.
3. Overriding `get_serializer_context` to pass bulk-fetched data (like a set of IDs for `is_in_wishlist`) to avoid per-object DB lookups.
4. Using `hasattr(obj, 'annotated_field')` in the serializer to check for pre-calculated values.
