## 2025-02-23 - Accessibility for Selection Groups
**Learning:** Selection groups (like packing sizes) implemented as buttons often miss semantic grouping.
**Action:** Use a wrapper with `role="group"` and `aria-label`, and use `aria-pressed` on the individual buttons to indicate the selected state. This makes the interaction clear to screen reader users.
