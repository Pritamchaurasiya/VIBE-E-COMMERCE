## 2025-05-23 - Default Permissions and N+1 Optimization
**Learning:** `config/settings.py` sets `REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES']` to `IsAuthenticated`, which implicitly protects all views that don't explicitly override it. This can cause tests to fail with 401/403 for views intended to be public if `permission_classes = [AllowAny]` is omitted.
**Action:** Always check `DEFAULT_PERMISSION_CLASSES` in settings and explicitly set `permission_classes` on public views to ensure intended access control.

**Learning:** Optimizing DRF serializers with `prefetch_related` and annotations requires careful handling of serializer methods. `aggregate()` calls in serializer methods defeat prefetching; annotations must be used instead.
**Action:** When optimizing count/average fields in serializers, annotate the queryset in the view and check for the annotated attribute in the serializer method before falling back to aggregation.
