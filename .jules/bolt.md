## 2024-05-24 - N+1 Queries on Wishlist Checks
**Learning:** Checking existence in a reverse ManyToMany relation (e.g., `if user in product.wishlisted_by.all`) inside a template loop triggers a database query for every item.
**Action:** Fetch the set of related IDs (e.g., `user_wishlist_ids`) in the view using `values_list('product_id', flat=True)` and check membership in that set within the template (e.g., `if product.id in user_wishlist_ids`). This reduces O(N) queries to O(1) query.
