## 2024-05-20 - Accessibility in Product Selection
**Learning:** Adding `aria-pressed` to selection buttons (like product packing size) significantly improves screen reader experience by clarifying which option is currently active, without relying on visual cues.
**Action:** When implementing custom selection components (that aren't standard radio buttons or selects), always ensure the "selected" state is programmatically exposed via `aria-pressed` (for toggles) or `aria-selected` (for tabs/lists) and provide clear `aria-label`s.
