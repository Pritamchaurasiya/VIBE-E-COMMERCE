## 2024-05-22 - Optimizing DRF Serializers with Context
**Learning:** In Django Rest Framework, passing bulk-fetched data (like a set of IDs) via `serializer_context` is a powerful way to eliminate N+1 queries for per-object checks (like `is_in_wishlist`). This is often cleaner than trying to annotate boolean flags onto the queryset, especially when the check depends on the request user.
**Action:** Always check `serializer_context` first in `SerializerMethodField` implementations before hitting the database.

## 2024-05-22 - Handling Annotated Values in Serializers
**Learning:** When using `annotate()` in views to optimize serializers, `SerializerMethodField` methods must explicitly check for the existence of the annotated attribute (using `hasattr`). If the attribute exists but is `None` (e.g. `Avg('rating')` with no reviews), the method should handle it gracefully (return 0 or default) instead of falling back to the original N+1 query.
**Action:** Use `if hasattr(obj, 'annotated_field'): return obj.annotated_field or default` pattern in serializers.
