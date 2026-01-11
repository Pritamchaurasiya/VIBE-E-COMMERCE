# Bolt's Journal

## 2024-05-22 - Initial Entry
**Learning:** Performance optimizations should be targeted and measurable.
**Action:** Always verify N+1 queries in Django and unnecessary re-renders in React.

## 2024-05-22 - N+1 Optimization in RecommendationService
**Learning:** Django ORM's `select_related` and `prefetch_related` are essential for optimizing querysets that are serialized or accessed in loops. Without them, iterating over products to access `category`, `vendor`, or reverse relationships like `images` triggers N+1 queries.
**Action:** Always apply `.select_related()` for ForeignKey fields and `.prefetch_related()` for ManyToMany/Reverse relationships when the queryset will be serialized or iterated over. Verified reduction from ~31 queries to 2 queries for a list of 10 items.
