## 2024-05-22 - Broken Currency Symbols
**Learning:** Multiple frontend components (`SearchAutocomplete`, `AgriProductCard`, `ProductDetail`, `ProductList`) displayed the Indian Rupee symbol as `Ã¢â€šÂ¹` (mojibake) or `?`. This suggests source files were likely saved with an encoding that didn't match the build process or browser interpretation (e.g., CP1252 vs UTF-8).
**Action:** Always use the Unicode escape sequence `\u20B9` for the Indian Rupee symbol in JSX/JS files to ensure consistent rendering across all environments and avoid encoding-related corruption.
