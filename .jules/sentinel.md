# Sentinel's Journal 🛡️

## 2025-01-17 - [Header Injection in Export Data]
**Vulnerability:** Header Injection (HTTP Response Splitting) in `admin_export_data` view.
**Learning:** The view blindly concatenated user input (`export_type`) into the `Content-Disposition` header. While Django protects against newline injection preventing full response splitting, the filename parameter could be manipulated to spoof file extensions (e.g., .exe instead of .csv), leading to potential social engineering attacks.
**Prevention:** Always validate user input against a whitelist when using it in HTTP headers, especially `Content-Disposition`.
