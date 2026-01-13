# Bolt's Journal

## 2024-05-22 - Optimizing RecommendationsView
**Learning:** Manual serialization of related objects (e.g., `p.category.name`, `p.vendor.name`) in a loop without `select_related` causes severe N+1 query issues (22 queries for 8 items). Also, using sliced querysets in `exclude(id__in=...)` generates inefficient subqueries.
**Action:** Use `select_related` for all related fields accessed in loops. For exclusion lists from sliced querysets, evaluate them to a list of IDs first to avoid subqueries.
