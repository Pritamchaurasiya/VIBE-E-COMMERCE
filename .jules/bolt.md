## 2024-05-23 - N+1 in Manual Serializers
**Learning:** DRF serializers handle `select_related` automatically if configured, but manual list comprehensions in views (like `RecommendationsView`) completely bypass this.
**Action:** Always check views that manually construct response dictionaries. If they access related fields (like `p.category.name`), they MUST use `select_related` in the queryset.
