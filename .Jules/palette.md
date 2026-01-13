## 2026-01-13 - [Environment Integrity Check]
**Learning:** Always verify the integrity of critical asset files (like CSS) and check for missing dependencies in the existing codebase before implementing new features. Corrupted or missing files can cause confusing build errors that mask the actual issues.
**Action:** When starting a task, run a build or lint check on the unmodified codebase to identify existing environment issues (like missing `lucide-react` or corrupted CSS) so they can be addressed as prerequisites.
