## 2025-01-30 - Fix for N+1 queries in Product List API

**Learning:**
The `ProductListView` had severe N+1 query issues because the `ProductSerializer` was accessing related fields (`images`, `reviews`) without prefetching. Additionally, `get_average_rating` in the serializer was evaluating the entire `reviews` queryset (`if reviews:`) just to check for existence, which loads all reviews into memory, before running an aggregation query.

**Action:**
1.  Used `prefetch_related('images')` in `ProductListView`.
2.  Annotated `average_rating`, `review_count` and `is_in_wishlist` (via `Exists` subquery) in the queryset.
3.  Updated `ProductSerializer` to use these annotated fields if present, avoiding N+1 queries.
4.  Removed the inefficient `if reviews:` check in `ProductSerializer`.
5.  Added a regression test `store/tests/test_performance_product_list.py` ensuring query count remains low (3 queries vs ~50 for 10 items).
