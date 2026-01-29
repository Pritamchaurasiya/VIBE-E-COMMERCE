# Palette's Journal

## 2025-02-18 - BOM in Source Files
**Learning:** Some source files (like `Header.js`) contain a Byte Order Mark (BOM), which causes automated patch tools and git merge diffs to fail if not stripped.
**Action:** Always check for BOM or hidden characters when diffs fail unexpectedly on seemingly identical lines. Use tools that strip BOM or handle encoding gracefully.

## 2025-02-18 - Inconsistent Search Implementation
**Learning:** The `Header` component uses a raw `InputBase` for search, bypassing the robust `SearchAutocomplete` component available in `common`. This leads to missed functionality (suggestions, history) and requires duplicate accessibility work.
**Action:** Future refactor should replace the manual input with `SearchAutocomplete` for a consistent experience and better accessibility defaults.
