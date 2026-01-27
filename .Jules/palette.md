## 2025-01-27 - SearchAutocomplete Accessibility & Encoding
**Learning:** Found critical issues in `SearchAutocomplete.js`:
1. `Typography` used as a button without `role="button"` or keyboard handlers.
2. File contained a Byte Order Mark (BOM) causing linter warnings.
3. Currency symbols were rendered as mojibake (`Ã¢â€šÂ¹`) instead of proper Unicode.

**Action:**
- When converting designs, ensure interactive elements use Semantic HTML (`<button>`) or full ARIA attributes.
- Verify file encoding (UTF-8 w/o BOM) to prevent rendering artifacts.
- Use Unicode escape sequences (e.g., `\u20B9`) for special characters in JSX to ensure consistency.
