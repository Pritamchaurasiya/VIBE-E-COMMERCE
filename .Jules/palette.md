## 2024-05-22 - [Keyboard Shortcuts for Search]
**Learning:** Users expect global shortcuts (like `/` or `Ctrl+K`) for primary actions like search, but implementing them requires careful checks (`document.activeElement`) to avoid hijacking focus from other inputs.
**Action:** Always wrap global keydown listeners with checks for `INPUT`, `TEXTAREA`, and `isContentEditable` to preserve standard typing behavior.
