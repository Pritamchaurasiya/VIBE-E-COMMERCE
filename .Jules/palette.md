## 2024-05-22 - List View Accessibility Gaps
**Learning:** Cart and List components consistently lack aria-labels for repeated actions (checkboxes, quantity controls), making them unusable for screen readers.
**Action:** Always check `map()` iterations for interactive elements and ensure they have unique, descriptive labels (e.g., include item name).
