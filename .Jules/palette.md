# Palette's Journal - Critical UX Learnings

Format: `## YYYY-MM-DD - [Title]
**Learning:** [UX/a11y insight]
**Action:** [How to apply next time]`

## 2024-05-23 - Mojibake in Currency Symbols
**Learning:** The application uses `Ã¢â€šÂ¹` or `?` as a placeholder for the Indian Rupee symbol (`₹`) in several components, leading to confusing pricing displays. This is likely due to encoding mismatches in source files.
**Action:** Manually correct these to `\u20B9` or `₹` in `AgriProductCard.js`, `SearchAutocomplete.js`, and `ProductDetail.js` to ensure consistent and professional currency formatting.

## 2024-05-23 - Missing ARIA Labels on Icon Buttons
**Learning:** Interactive elements like the "Clear search" button in `SearchAutocomplete` lack `aria-label` attributes, making them inaccessible to screen reader users who only hear "button".
**Action:** Systematically audit icon-only buttons and add descriptive `aria-label` attributes (e.g., `aria-label="Clear search"`).
