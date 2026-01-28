## 2025-02-17 - N+1 in DRF Serializers
**Learning:** `ProductSerializer` methods (`get_average_rating`, `get_review_count`, `get_is_in_wishlist`) were causing N+1 queries. Specifically, `if obj.reviews:` evaluates the entire queryset.
**Action:** Use `prefetch_related` and `annotate` in views (`ProductListView`). Update serializer methods to check for annotated attributes (e.g. `hasattr(obj, 'annotated_avg_rating')`) before falling back to DB queries. Avoid boolean evaluation of RelatedManagers.
