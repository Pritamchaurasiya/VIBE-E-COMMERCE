## 2025-02-04 - Unoptimized Product List
**Learning:** ProductListView generates ~27 queries for 5 products due to missing prefetch for 'images' and N+1 queries for 'average_rating', 'review_count', and 'is_in_wishlist'. 'requirements.txt' incorrectly requested Django 6.0 causing conflicts.
**Action:** Always verify query counts for lists using serializer method fields.
