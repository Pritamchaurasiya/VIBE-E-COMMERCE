## 2024-05-23 - Keyboard Shortcuts
**Learning:** Adding keyboard shortcuts (like `/` for search) provides significant value to power users but requires careful implementation to avoid hijacking input in form fields (`INPUT`, `TEXTAREA`).
**Action:** Always check `document.activeElement.tagName` before preventing default behavior for single-key shortcuts.

## 2024-05-23 - Character Encoding in React
**Learning:** Using raw special characters (like ₹ or •) in JSX files can lead to mojibake/encoding issues depending on the build environment.
**Action:** Always use Unicode escape sequences (e.g., `\u20B9`, `\u2022`) in JSX to ensure consistent rendering across all platforms.
