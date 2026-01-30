## 2026-01-30 - Keyboard Shortcuts for Search
**Learning:** Power users expect keyboard shortcuts (like `/` or `Ctrl+K`) for global search. Adding visual hints (like `(/)` in placeholder) significantly aids discoverability without cluttering the UI.
**Action:** When implementing global search bars, always add a `ref` and `keydown` listener for `/` and `Ctrl+K`. Ensure the listener respects `document.activeElement` to avoid hijacking focus from other inputs.
