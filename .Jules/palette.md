## 2026-01-25 - Accessibility of Custom Toggle Groups & Currency Symbols
**Learning:** Custom buttons acting as radio groups (like packing options) require `role="group"` and `aria-pressed` to be understandable by screen readers. Visual indication via CSS classes is insufficient.
**Action:** Always wrap related toggle buttons in a group with a label and explicitly manage `aria-pressed` state.

**Learning:** Source code containing literal currency symbols (like `₹`) can be corrupted into `?` due to encoding mismatches (Windows-1252 vs UTF-8).
**Action:** Use Unicode escape sequences (e.g., `\u20B9`) for special characters in source code to ensure consistent rendering across all environments.
