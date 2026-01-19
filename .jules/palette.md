## 2025-02-23 - Packing Options Accessibility
**Learning:** Toggle button groups (like packing sizes) implemented as separate buttons often lack state indication for screen readers.
**Action:** Use `aria-pressed` for button-based toggles or `role="radio"` for mutually exclusive options to ensure the selected state is communicated.
