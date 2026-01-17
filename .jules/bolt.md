## 2025-02-22 - Optimizing ProductListView N+1 Queries
**Learning:**
N+1 queries were a significant bottleneck in `ProductListView` (approx 52 queries for 10 products). This was due to:
1.  Accessing `product.images.all()` in `ProductSerializer` without `prefetch_related('images')`.
2.  Calculating `avg_rating` and `review_count` in `ProductSerializer` methods using aggregate queries for each instance.
3.  Checking `Wishlist.objects.filter(user=request.user, product=obj).exists()` for every product in the list.

**Action:**
1.  Used `prefetch_related('images')` in `ProductListView.get_queryset`.
2.  Used `annotate(avg_rating=Avg('reviews__rating'), review_count_annotated=Count('reviews'))` in the queryset to fetch these stats in the main query.
3.  Updated `ProductSerializer` to check for these annotations/prefetches and use them if available, falling back to DB queries only if necessary (for detail views, etc.).
4.  Overrode `get_serializer_context` in `ProductListView` to fetch all `wishlist_product_ids` for the user in a single query and pass it to the serializer context. The serializer now checks this set in O(1) time instead of querying the DB.

**Result:**
Reduced queries for listing 10 products from ~52 to 4. This scales O(1) with respect to page size instead of O(N).

**Caveat:**
When testing N+1 query reductions with `CaptureQueriesContext`, ensure `DEBUG=True` is set in the test environment, otherwise `connection.queries` is not populated. Also, `client.force_authenticate` might trigger profile creation signals or session logic that adds a constant overhead (2-3 queries), so account for that in assertions.
