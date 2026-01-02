# Bolt's Journal

## 2024-10-26 - Django N+1 Queries
**Learning:** Checking `if user in product.wishlisted_by.all` in templates causes N+1 queries because it executes a separate query for each product in the loop.
**Action:** Fetch a set of `product_id`s from the `Wishlist` model in the view and check membership in the template using a variable like `user_wishlist_ids`.

## 2024-10-27 - Frontend List Rendering
**Learning:** Rendering long lists of products without virtualization causes significant DOM size and re-render performance issues.
**Action:** When seeing `map` over large arrays in React, consider if `react-window` or pagination should be applied, but stick to small changes first like `React.memo`.

## 2024-10-27 - Django Count Optimization
**Learning:** Doing multiple `count()` queries on the same QuerySet with different filters is inefficient.
**Action:** Use a single `aggregate()` call with `Count('id', filter=Q(...))` to get multiple counts in one DB hit.
