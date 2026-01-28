## 2024-05-22 - Django N+1 in DRF Serializers
**Learning:** `SerializerMethodField` methods in DRF often cause N+1 queries if they access related managers (e.g., `obj.images.all()`) without prefetching. `select_related` and `prefetch_related` in the View's `get_queryset` are essential. For aggregated fields (count, avg), `annotate` in the queryset is vastly superior to python-side aggregation in the serializer.
**Action:** Always check `SerializerMethodField` implementations for database access and pair them with `prefetch_related` or `annotate` in the corresponding View.
