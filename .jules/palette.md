# 2026-01-29 - Power User Accessibility via Keyboard Shortcuts

**Learning:**
Power users and keyboard-first users often feel slowed down by requiring mouse interactions for common actions like search. Implementing global shortcuts (like `/` or `Ctrl+K`) creates a "delight" moment and significantly speeds up navigation without cluttering the UI. However, it's critical to ensure these shortcuts don't hijack focus when the user is already typing in another input field (checking `document.activeElement`).

**Action:**
When adding search or navigation features in the future, always consider adding a keyboard shortcut. ensure it is documented (e.g., via placeholder text or tooltip) so users can discover it. Always guard against `activeElement` to prevent frustration.
