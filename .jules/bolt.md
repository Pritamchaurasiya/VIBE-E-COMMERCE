## 2025-02-19 - Dashboard Optimization & Bug Fixes
**Learning:** `Count()` aggregation must use the `related_name` (e.g., `'products'`) if defined, not the model name. Django does not fallback to model name in reverse relations when `related_name` is set.
**Action:** Always check `related_name` in models before writing aggregations.

**Learning:** `store/tracking_service.py` was attempting to import from a non-existent `tracking_models` module and using `triggered_by` as a direct keyword argument for `TrackingAlert`, which caused crashes.
**Action:** Verified and fixed imports and model usage.

**Learning:** Conditional aggregation in Django (using `filter=Q(...)` inside `Sum` or `Count`) significantly reduces query count for dashboard-like views compared to Python-side loops or multiple filtered queries.
**Action:** Use conditional aggregation for statistical summaries.
