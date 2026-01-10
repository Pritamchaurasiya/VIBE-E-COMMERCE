## 2024-05-23 - N+1 Queries in DRF Serializers
**Learning:** DRF `SerializerMethodField` often hides N+1 queries. Specifically, accessing related models (like `obj.images.all()`) or running aggregates inside a serializer method runs a query for *every* item in the list.
**Action:**
1. Use `prefetch_related` and `annotate` in the `View.get_queryset` method to fetch all data in 1-2 queries.
2. In the Serializer, check if the data is already available (e.g., `hasattr(obj, 'annotated_field')` or checking context) before running a query.
3. Pass expensive lookup data (like `wishlist_product_ids`) via `serializer_context`.
