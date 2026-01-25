# Palette's Journal 🎨

## 2024-05-22 - Currency Symbol Encoding
**Learning:** The application uses `?` or mangled characters like `Ã¢â€šÂ¹` instead of the Indian Rupee symbol (`₹`) in several React components. This indicates a likely encoding issue or developer habit of using placeholders.
**Action:** Always verify currency symbols in the UI. Use `\u20B9` or the direct `₹` symbol (ensure file encoding is UTF-8) for consistency and trust.

## 2024-05-22 - Accessibility in Selection Groups
**Learning:** "Packing Options" (or size selectors) implemented as a list of buttons often lack semantic grouping. Screen readers treat them as unrelated buttons.
**Action:** Use `role="group"` with an `aria-label` for the container, and `aria-pressed` or `aria-selected` for the individual items to communicate state effectively.
