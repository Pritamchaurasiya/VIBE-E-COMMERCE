## 2024-05-22 - Pre-existing Test Failures in API Tests
**Learning:** When running regression tests, I discovered that `store.tests.test_api.ProductAPITest` (and others) fail with 401 Unauthorized, while the tests expect 200 OK. This indicates that `ProductListView` and `ProductDetailView` are missing `permission_classes = [permissions.AllowAny]`, relying on the default `IsAuthenticated`.
**Action:** When working on legacy codebases, always check the baseline test health before assuming failures are caused by recent changes. Future tasks should address these permission inconsistencies.
