## 2025-01-31 - [N+1 Query Bottleneck in Product List]
**Learning:** `ProductListView` had severe N+1 query issues (52 queries for 10 products) due to accessing `images` and `reviews` in the serializer without prefetching or annotation.
**Action:** Use `prefetch_related('images')` and `annotate` for review statistics in the queryset. Update serializers to check for annotated fields before falling back to related managers.
