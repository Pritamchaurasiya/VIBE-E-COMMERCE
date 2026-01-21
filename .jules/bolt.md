## 2024-05-23 - N+1 in SerializerMethodField and CSP 4.0
**Learning:** `SerializerMethodField` in DRF often causes N+1 queries when accessing reverse relationships (like `obj.images.all()`) if `prefetch_related` is not explicitly called in the view. Also, `django-csp` 4.0 requires dictionary-based settings and crashes with legacy tuple configuration.
**Action:** Always check `get_queryset` for `prefetch_related` when using nested serializers or `SerializerMethodField`. When updating dependencies, check for breaking configuration changes like CSP's dictionary format.
