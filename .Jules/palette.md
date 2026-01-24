## 2024-05-22 - Currency Encoding and Interactive Button Accessibility
**Learning:** The application uses `₹` (Indian Rupee) but source files often contain Mojibake (e.g., `?` or `Ã¢â€šÂ¹`). This requires manual correction in components. Also, dynamic "Add to Cart" buttons lack state announcements for screen readers.
**Action:** Always verify currency symbol rendering in the browser or via tests that check for the specific character. Use `aria-live="polite"` and dynamic `aria-label` for buttons that change text/state to ensure screen readers announce the update.
