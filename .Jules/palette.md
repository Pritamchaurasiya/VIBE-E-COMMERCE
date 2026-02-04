## 2025-02-27 - [Build Environment Isolation]
**Learning:** This repo has broken build dependencies (missing `prop-types`, `lucide-react`, `redux`) and configuration. While fixing them locally is necessary for verification (`pnpm build`), these fixes must NOT be included in the final PR if they violate 'No new dependencies' rules or are out of scope. Submit ONLY the UX improvement.
**Action:** In future tasks, separate local verification fixes from the final submission. Use `restore_file` to revert environment fixes before submitting.
