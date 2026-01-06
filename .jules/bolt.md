## 2024-05-22 - N+1 Queries in Recommendations
**Learning:** Manual serialization in API views (list comprehensions accessing foreign keys) often hides N+1 query problems that DRF Serializers might sometimes handle better (or worse, depending on configuration). Explicit `select_related` is crucial when manually building response dictionaries from related models.
**Action:** Always audit list comprehensions that iterate over model instances and access related fields (like `p.category.name`) to ensure the initial queryset has `select_related`.
