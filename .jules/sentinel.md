## 2026-01-10 - [CSV Injection Vulnerability in Exports]
**Vulnerability:** User-controlled fields (e.g., Name, Address, Email) exported to CSV via `ExportDataView` were not sanitized, allowing formula injection (CSV Injection).
**Learning:** Standard Django `csv.writer` does not automatically sanitize fields starting with dangerous characters like `=`, `+`, `-`, or `@`.
**Prevention:** Always use a helper function like `sanitize_csv_field` to prepend a single quote `'` to fields starting with these characters before writing them to CSV.
