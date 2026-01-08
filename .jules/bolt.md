# Bolt's Journal

## 2024-05-22 - Initial Setup
**Learning:** Performance journals help track what works and what doesn't.
**Action:** Always check for this file before starting work.
## 2024-05-23 - N+1 Query Optimization
**Learning:** Optimizing `SerializerMethodField` by using `annotate` on the queryset and checking for the attribute in the serializer is a powerful pattern to solve N+1 queries without breaking existing functionality.
**Action:** When seeing `SerializerMethodField` accessing related models, check if it can be annotated in the view's queryset.
