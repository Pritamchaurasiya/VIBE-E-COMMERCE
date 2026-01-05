## 2024-05-23 - Avoiding N+1 Queries in DRF
**Learning:**
- Use  for reverse foreign keys (like images, reviews) to fetch related objects in a single query.
- Use  for aggregating related data (like average rating, review count) directly in the database query instead of looping in Python.
- For checking existence (like ) in a list view, fetch all IDs for the user in one query and pass them to the serializer context to do O(1) lookups, instead of doing  query per object.
- **Critical:** When using  with  on a queryset that involves joins (e.g. ), always use  inside  (e.g. ) to avoid incorrect counts due to row multiplication.
**Action:** Always audit  in list views for potential N+1 queries.
## 2024-05-23 - Avoiding N+1 Queries in DRF
**Learning:**
- Use prefetch_related for reverse foreign keys to fetch related objects in a single query.
- Use annotate for aggregating related data directly in the database query instead of looping in Python.
- For checking existence (like is_in_wishlist) in a list view, fetch all IDs for the user in one query and pass them to the serializer context to do O(1) lookups.
- **Critical:** When using annotate with Count on a queryset that involves joins, always use distinct=True inside Count to avoid incorrect counts due to row multiplication.
**Action:** Always audit SerializerMethodField in list views for potential N+1 queries.
