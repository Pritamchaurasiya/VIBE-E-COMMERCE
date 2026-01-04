## 2025-05-12 - Icon-Only Button Accessibility
**Learning:** Icon-only buttons (like the "clear search" button) are a common accessibility trap. They visually communicate intent via an icon but leave screen reader users with unhelpful announcements like "button" unless explicitly labeled.
**Action:** Always check `IconButton` components for an `aria-label` attribute. If the button relies solely on an icon, adding `aria-label="Action description"` is mandatory.
