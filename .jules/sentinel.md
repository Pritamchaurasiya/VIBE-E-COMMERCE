## 2025-05-19 - CSV Injection (Formula Injection)
**Vulnerability:** CSV exports in `store/api_views.py` and `store/views.py` were writing user-controlled input (names, addresses, etc.) directly to CSV files without sanitization. This allowed Formula Injection (CSV Injection) where malicious input starting with `=`, `+`, `-`, or `@` could execute code in spreadsheet software (Excel, etc.).
**Learning:** Even internal admin exports are attack vectors if they process user data. Developers often overlook CSV sanitization assuming the file is text-only, but spreadsheet software interprets certain prefixes as formulas.
**Prevention:** Always sanitize data before writing to CSV. Prepend a single quote `'` to any field starting with dangerous characters to force it to be treated as a string.
