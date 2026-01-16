## 2024-05-22 - Custom Component Accessibility Gaps
**Learning:** Custom implementations of common UI patterns (like product cards in `HomePage.js`) often miss accessibility features (ARIA labels) that are present in reusable components (`AgriProductCard.js`).
**Action:** When auditing for accessibility, check page-specific component implementations first, as they are less likely to have been reviewed than shared library components.
