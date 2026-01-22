## 2024-05-22 - N+1 Optimization in ProductListView

**Learning:**
Standard Django REST Framework Serializers with `SerializerMethodField` are prone to N+1 query issues if they access related objects (like `obj.images.all()`) or aggregations (like `obj.reviews.aggregate()`) inside the method.

**Action:**
To fix this, use `queryset.prefetch_related()` and `queryset.annotate()` in the view's `get_queryset` method. Then, update the serializer to check for these prefetched/annotated values before hitting the database.

Also, fetching related user data (like wishlist items) should be done in bulk in the view and passed to the serializer context, rather than querying for each object in the serializer.

**Surprise:**
Even with `prefetch_related`, `obj.images.all()` works fine because it uses the prefetch cache. However, aggregations on related objects often trigger new queries unless explicitly annotated on the main queryset.
