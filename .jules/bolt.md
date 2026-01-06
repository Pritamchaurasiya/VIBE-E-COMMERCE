## 2024-05-22 - Optimizing Product List Queries
**Learning:** `prefetch_related` is not enough when serializers use computed properties that hit the database (like `reviews.aggregate()`).
**Action:** Use `queryset.annotate()` to pre-calculate these values (e.g., `Avg('reviews__rating')`, `Count('reviews')`) and update the serializer to use the annotated attributes if present. This reduces queries from O(N) to O(1) for list views.

## 2024-05-22 - Testing Permissions
**Learning:** `generics.ListAPIView` defaults to global `REST_FRAMEWORK` permissions (often `IsAuthenticated`). Public endpoints must explicitly set `permission_classes = [AllowAny]`.
**Action:** Always check default permissions when creating or modifying public-facing views.
