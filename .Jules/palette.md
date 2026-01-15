## 2024-05-23 - Missing Keyboard Navigation Links
**Learning:** Even when documentation or memory suggests an accessibility feature like "Skip to Main Content" exists, it might be missing or implemented incorrectly. Always verify with code inspection or manual testing.
**Action:** When auditing accessibility, start by checking for the presence and functionality of the "Skip to Content" link as it's the first element keyboard users interact with.

## 2024-05-23 - Build System Fragility
**Learning:** The frontend build system was fragile, with missing dependencies (`redux`, `lucide-react`, `prop-types`) and syntax errors in generated or copied code (`globalThis` in service worker, missing exports).
**Action:** Always run a full build (`pnpm build`) after making changes, even small ones, to catch environment and dependency issues that might not appear in development mode.
