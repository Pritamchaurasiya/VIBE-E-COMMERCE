## 2024-05-23 - Django N+1 in DRF Serializers
**Learning:** In Django Rest Framework, standard `SerializerMethodField` or properties on models often trigger N+1 queries if they access related objects (like `product.reviews` or `product.category`) without prefetching in the view.
**Action:** Always check `get_queryset` in views for `select_related`/`prefetch_related` when using serializers that access related fields. Use `django-debug-toolbar` or query counting tests to verify.

## 2024-05-23 - React Context Performance
**Learning:** Putting rapidly changing state (like scroll position or real-time input) into a high-level React Context triggers re-renders for ALL consumers, even those not using that specific data.
**Action:** Split contexts by update frequency or use libraries like `zustand` or `jotai` for atomic state updates to avoid unnecessary re-renders.

## 2024-05-23 - Django N+1 Baseline
**Learning:** The baseline query count for product list is 82 for 20 products, which confirms significant N+1 issues (likely 4 per product: images, avg_rating, review_count, wishlist).
**Action:** Optimize `ProductListView` with `prefetch_related` and annotations.
