## 2024-05-23 - [Frontpage Stats Caching]
**Learning:** High-traffic pages like the homepage often have expensive aggregate queries (like counts) that don't need to be real-time. Caching these can significantly reduce DB load.
**Action:** Always look for `count()` or `aggregate()` calls on frequently accessed views and consider caching them if real-time accuracy isn't critical.
