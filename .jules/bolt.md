## 2024-05-22 - Optimizing N+1 Queries in Django DRF
**Learning:** `prefetch_related` combined with `annotate` and context injection can drastically reduce database queries in list views.
**Action:** Always check `SerializerMethodField` implementations for potential N+1 queries. Use `django.test.utils.CaptureQueriesContext` to verify query counts in tests. Inject bulk data (like wishlist status) into serializer context instead of querying per object.
