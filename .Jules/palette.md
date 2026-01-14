## 2024-05-22 - Icon-Only Buttons Missing Labels
**Learning:** Several `IconButton` and `Fab` components in `ProductList.js` were missing `aria-label`s, relying solely on icons which are invisible to screen readers. This seems to be a common pattern in the product list implementation.
**Action:** When working with Material UI components, especially `IconButton` and `Fab`, always check for and add `aria-label` if no text label is present.
