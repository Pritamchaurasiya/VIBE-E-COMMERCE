## 2024-05-23 - N+1 Queries in DRF Serializers
**Learning:** Checking relationships in `SerializerMethodField` (like `Wishlist.objects.filter(user=request.user, product=obj)`) inside a List View causes massive N+1 query issues.
**Action:** Use `get_serializer_context` in the View to fetch all necessary related IDs (e.g., `wishlist_product_ids`) in a single query, pass them to the serializer context, and perform O(1) lookups in the serializer. Also, leverage `annotate` for counts/averages instead of querying per object.
