## 2025-02-18 - N+1 Query Optimization in ProductListView

**Learning:**
The `ProductListView` suffered from a significant N+1 query problem, executing ~5 queries per product (images, wishlist status, ratings, reviews). This resulted in over 100 queries for a page of 20 products.

**Action:**
1.  **Use `prefetch_related`:** Added `queryset.prefetch_related('images')` to fetch related images in a single query.
2.  **Use Annotations:** Replaced python-side aggregation for `avg_rating` and `review_count` with database-side `annotate()` using `models.Avg` and `models.Count`. Updated `ProductSerializer` to use these annotated attributes.
3.  **Preload Context:** Implemented `get_serializer_context` in the view to fetch all wishlist product IDs for the current user in a single query, eliminating per-product wishlist lookups.
4.  **Middleware/Test Issues:** Discovered that `SecurityTrackingMiddleware` runs before `SessionMiddleware`, causing `AttributeError` when accessing `request.session`. Also found `tracking_models` import issues. Fixed `tracking_service.py` to handle missing session safely and correct imports.

**Result:**
Query count for listing 20 products dropped from **102** to **4**. Response time improved significantly (~3.5x faster in micro-benchmark).
