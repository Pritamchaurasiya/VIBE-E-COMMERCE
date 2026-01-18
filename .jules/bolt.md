# Bolt's Journal

## 2024-05-22 - [Initial Setup]
**Learning:** Establishing the performance journal.
**Action:** Use this file to record critical performance learnings as defined in the system prompt.

## 2024-05-22 - [Cart Query Optimization]
**Learning:** `Cart` class was re-fetching products multiple times (in `__iter__` and `get_total_cost`) even though they were already fetched in `__init__` (for DB cart) or could be batched. This caused N+1 issues and redundant queries.
**Action:** Implemented a `products_cache` in `Cart` to store `Product` instances. This reduced Cart API queries from 3 to 1 per request. Also optimized `CartView` to avoid calling `get_total_cost` which iterates again.
