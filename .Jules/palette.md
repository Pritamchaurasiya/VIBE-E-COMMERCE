## 2025-02-20 - Critical Build Fixes and UX
**Learning:** The `frontend/src/styles/agri-theme.css` file was corrupted with null bytes (`\000`) and missing braces, causing webpack build failures.
**Action:** When encountering "Unknown word" errors in CSS, check for binary corruption or encoding issues.

**Learning:** `frontend/package.json` contained `"type": "commonjs"`, which conflicts with `react-scripts` (Create React App) causing "import and export may appear only with sourceType: module" errors.
**Action:** Ensure `package.json` does not enforce CommonJS for CRA projects.

**Learning:** Missing dependencies (`lucide-react`, `prop-types`, `redux`) caused compilation failures in existing components (`MonitoringDashboard`, `AuthContext`).
**Action:** Verify all imported libraries are present in `package.json`.
