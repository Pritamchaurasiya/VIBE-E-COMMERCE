## 2025-02-20 - N+1 in Serializer Methods
**Learning:** `prefetch_related` does NOT prevent N+1 queries when using `related_manager.aggregate()` or `.count()` inside a serializer method. These operations trigger new SQL queries even if the related objects are prefetched.
**Action:** Use `queryset.annotate()` to calculate aggregates in the main query and update the serializer to use these annotated values if available.

## 2025-02-20 - Default Permissions and Testing
**Learning:** When `DEFAULT_PERMISSION_CLASSES` is set to `IsAuthenticated`, public views must explicitly set `permission_classes = [AllowAny]`. Tests using `APIClient` without authentication will fail with 401 if this is missing, even if the view logic implies public access.
**Action:** Always verify `permission_classes` on public views and ensure tests cover unauthenticated access for public endpoints.
