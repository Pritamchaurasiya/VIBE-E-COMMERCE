## 2024-05-23 - N+1 Queries in Product List
**Learning:** DRF Serializers with SerializerMethodField often cause N+1 queries if underlying relationships aren't prefetched. Specifically, `ProductSerializer` triggered queries for images, reviews, and wishlist status for every row.
**Action:** Always audit `SerializerMethodField` implementations. Use `prefetch_related` and `annotate` in the View's queryset. Use `serializer_context` to pass bulk-fetched data (like wishlist status) to serializers.
