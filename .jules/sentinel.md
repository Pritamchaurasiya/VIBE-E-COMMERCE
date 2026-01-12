## 2024-05-22 - CSV Injection Vulnerability
**Vulnerability:** User-controlled data (e.g., first_name) starting with `=`, `+`, `-`, or `@` was exported directly to CSV files in `ExportDataView`.
**Learning:** Even sanitized input (HTML-safe via `bleach`) can be dangerous in different contexts like CSV exports (Formula Injection). `bleach.clean` does not protect against CSV injection.
**Prevention:** Always sanitize data specifically for the output format. For CSVs, prepend a single quote `'` to values starting with dangerous characters. Created reusable `sanitize_csv_field` utility in `store/utils/security.py`.
