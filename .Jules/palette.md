## 2024-05-22 - [Hidden Costs of Duplication]
**Learning:** Inlining UI components (like product cards in HomePage) instead of reusing dedicated components (`AgriProductCard`) often leads to accessibility regressions (missing ARIA labels).
**Action:** Always audit pages for inline component implementations and refactor or strictly enforce accessibility parity with the source of truth component.
