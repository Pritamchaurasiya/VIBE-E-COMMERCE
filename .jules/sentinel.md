## 2025-02-18 - SQL Injection False Positives in Regex
**Vulnerability:** The `SQL_INJECTION_PATTERN` regex in `store/tracking_service.py` included `|@|`, causing valid email addresses to be flagged as SQL injection attempts.
**Learning:** Overly aggressive regex patterns for security detection can lead to false positives, disrupting legitimate user actions (like using an email address).
**Prevention:** When creating blocklists or detection patterns, carefully review common valid inputs (like emails) to ensure they don't trigger the detection. Use `@@` for SQL variable detection instead of single `@`.
