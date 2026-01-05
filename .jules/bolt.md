## 2024-12-12 - N+1 Query in Recommendations
**Learning:** `RecommendationsView` iterates over product querysets to build a response list, accessing `p.category.name` and `p.vendor.name`. Without `select_related`, this causes N+1 queries.
**Action:** Use `select_related('category', 'vendor')` in all querysets (`category_products`, `vendor_products`, `price_products`) that are iterated over and serialized with related field access.
