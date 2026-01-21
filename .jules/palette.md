## 2024-05-23 - Interactive Element Accessibility
**Learning:** Custom interactive elements (like packing size toggles and icon-only buttons) consistently lack `aria-label` and `aria-pressed` states in this codebase, relying solely on visual cues (CSS classes like `.active`).
**Action:** When touching any interactive component, blindly check for `aria-label` and `aria-pressed`/`aria-expanded` attributes, as they are likely missing.
