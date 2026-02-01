## 2025-02-18 - Input Focus Hijacking Prevention
**Learning:** When implementing global keyboard shortcuts (like `/` for search), explicitly check `document.activeElement` to ensure the user isn't already typing in a form field. Failing to do so frustrates users by hijacking their input.
**Action:** Always wrap global keydown listeners with `if (!['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName))` or similar logic.

## 2025-02-18 - Broken Dependency Chains
**Learning:** The frontend build system was fragile with missing dependencies (`redux`, `lucide-react`, `prop-types`) and corrupted CSS.
**Action:** When working on a legacy/unstable repo, anticipate spending time stabilizing the build environment before implementing features. Use `pnpm install` and check for missing peer dependencies early.
