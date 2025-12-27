## 2024-05-24 - N+1 Queries on Review List
**Learning:** Accessing `related_model.count()` (like `review.helpful_votes.count()`) in a loop triggers a database query for each item, causing N+1 issues. This is often hidden in properties or methods.
**Action:** Use `annotate(count_field=Count('related_field'))` in the queryset and update the model property to use `hasattr(self, 'count_field')` to return the annotated value if available, falling back to the query if not.
