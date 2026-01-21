## 2025-02-18 - Manual List Concatenation N+1
**Learning:** When constructing a response list by concatenating multiple querysets (e.g. `list(qs1) + list(qs2)`), ensure each source queryset uses `select_related` or `prefetch_related`. Django's lazy evaluation is triggered by `list()`, and subsequent iteration over the combined list will trigger N+1 queries if related fields aren't eager loaded.
**Action:** Always check `select_related` on querysets that are converted to lists for response merging.
