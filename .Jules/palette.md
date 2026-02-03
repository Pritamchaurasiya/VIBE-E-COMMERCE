# Palette's Journal

## Critical UX/Accessibility Learnings


## 2024-05-22 - Broken Test Environment
**Learning:** The frontend project was missing `@testing-library` packages in `devDependencies`. Even after installing them, `react-scripts test` fails with Babel syntax errors for JSX, suggesting a broken build/test configuration in the environment.
**Action:** When adding tests, verify the test runner works first. If the environment is broken, focus on manual verification and linting, and document the infrastructure issue.
