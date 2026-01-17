## BOLT JOURNAL
## 2024-05-23 - [Eliminate N+1 queries in Product List]
**Learning:**  when using  usually means  is not propagated correctly or query logging is disabled. When  was forced,  still appeared. The issue was likely due to the test running against a view that returned 401 Unauthorized (which does 0 product queries) instead of the expected 200 OK path. Always check response status code when debugging  failures.
**Action:** Always assert  before  to ensure the view logic was actually executed.
## 2024-05-23 - [Eliminate N+1 queries in Product List]
**Learning:** AssertionError: 0 != 21 when using assertNumQueries usually means DEBUG=True is not propagated correctly or query logging is disabled. When DEBUG=True was forced, 0 queries executed still appeared. The issue was likely due to the test running against a view that returned 401 Unauthorized (which does 0 product queries) instead of the expected 200 OK path. Always check response status code when debugging assertNumQueries failures.
**Action:** Always assert response.status_code before assertNumQueries to ensure the view logic was actually executed.
