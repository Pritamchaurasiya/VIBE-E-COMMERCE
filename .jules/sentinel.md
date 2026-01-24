## 2025-01-24 - CSV Formula Injection
**Vulnerability:** CSV Formula Injection (Formula Injection) in data export features (`ExportDataView` and `admin_export_data`). User-controlled input (names, emails) was written directly to CSV files, allowing malicious payloads starting with `=`, `+`, `-`, or `@` to be executed by spreadsheet software.
**Learning:** Even with HTML sanitization (`bleach`), other injection vectors like CSV injection must be handled separately. The codebase had documentation suggesting sanitization existed but the implementation was missing.
**Prevention:** Always sanitize data before exporting to CSV. Implemented `sanitize_for_csv` to prefix risky characters with `'`.
