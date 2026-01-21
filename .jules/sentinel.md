## 2025-02-19 - URL Pattern Shadowing
**Vulnerability:** URL pattern conflict causing 404s for specific endpoints. `api/v1/flash-sales/active/` was shadowed by `api/v1/flash-sales/<slug:slug>/`.
**Learning:** Always place specific URL patterns before generic slug-based patterns. Django resolves URLs in order.
**Prevention:** Review URL configuration order, especially when mixing specific paths and slug/ID paths.
