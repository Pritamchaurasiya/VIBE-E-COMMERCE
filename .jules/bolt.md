## 2024-03-22 - Optimizing ProductListView Query Count
**Learning:** The `ProductListView` had an N+1 query issue where fetching 10 products resulted in ~52 queries. This was due to accessing `product.images.all()`, `product.reviews.all()`, and `Wishlist.objects.filter(user=user, product=product).exists()` inside the serializer for each item.
**Action:**
1. Used `prefetch_related('images')` in `get_queryset` to fetch images in one batch.
2. Used `annotate(annotated_avg_rating=Avg('reviews__rating'), annotated_review_count=Count('reviews'))` to calculate aggregates in the main query, avoiding `reviews` prefetch (saving memory and a query).
3. Optimized `is_in_wishlist` by fetching all wishlist product IDs for the user in `list()` and passing them via `serializer_context`, changing an O(N) database operation to an O(1) set lookup in memory.
4. Reduced query count from 52 to 4 for a page of 10 products.
