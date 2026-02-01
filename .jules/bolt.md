## 2025-02-19 - [Django N+1 Optimization]
**Learning:** `ProductListView` suffered from severe N+1 queries (100+ queries for 20 items) due to accessing `images` and review aggregates in the serializer without prefetching/annotation.
**Action:** Implemented `prefetch_related('images')` and annotated `average_rating`, `review_count`, and `is_in_wishlist` (via `Exists` subquery) in `get_queryset`. Updated `ProductSerializer` to consume these annotations if present.

## 2025-02-19 - [Testing with Throttling & Redis]
**Learning:** Django tests running without a live Redis instance fail if DRF throttling is enabled or if `AXES` is active, as they attempt to connect to the configured Redis cache.
**Action:** When writing tests that involve views with throttling, use `@override_settings` to disable throttling (`DEFAULT_THROTTLE_CLASSES=[]`), set `AXES_ENABLED=False`, and switch `CACHES` to `LocMemCache`.
