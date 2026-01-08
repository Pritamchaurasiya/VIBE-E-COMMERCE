## 2024-05-22 - Identifying N+1 in RecommendationsView
**Learning:** Using select_related on the initial queryset is not enough when subsequent filtering involves related fields on *new* querysets constructed from the initial one or when iterating and accessing related fields that were not selected.
**Action:** Always check how the data is being accessed in the serialization or response construction phase. If manual dictionary construction is used, ensure all accessed related fields are pre-fetched.
