## 2024-05-23 - Accessibility in Toggle Buttons
**Learning:** Toggle buttons implemented as generic buttons with active classes are inaccessible to screen readers. They need aria-pressed to indicate state and specific aria-labels if the text content is ambiguous.
**Action:** Always verify custom toggle components have semantic state attributes.
