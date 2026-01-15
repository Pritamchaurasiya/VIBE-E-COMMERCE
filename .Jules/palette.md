## 2025-10-26 - Material UI Icon-Only Components
**Learning:** Material UI components like `Fab`, `IconButton`, and `Checkbox` (when used standalone) often lack visible text labels, making them inaccessible to screen readers by default. The `Tooltip` component provides a visual label on hover but does not consistently expose the accessible name to all assistive technologies unless `aria-label` is explicitly set on the interactive element itself.
**Action:** Always add `aria-label` to `Fab`, `IconButton`, and `Checkbox` (via `inputProps`) when they don't have accompanying text labels.
