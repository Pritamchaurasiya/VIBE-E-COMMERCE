## 2025-02-18 - Currency Symbol Encoding and ARIA gaps
**Learning:** The application attempts to display the Indian Rupee symbol but often renders as `?` or mojibake in source code. Also, custom interactive components like packing options in `AgriProductCard` lack semantic ARIA attributes.
**Action:** Always use the unicode escape sequence `\u20B9` for ₹ in JSX. Ensure custom selection groups (like packing sizes) use `role="group"` and `aria-pressed` or `aria-selected`.
