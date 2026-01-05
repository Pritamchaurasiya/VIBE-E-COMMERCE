## 2026-01-05 - Next.js Conflict

**Learning:** This project is a Create React App (CRA) but had `next` installed as a dependency, causing severe conflicts with `react-scripts`. Removing `next` was critical to restoring the build process.

**Action:** Always verify the project type (CRA vs Next.js) by checking `package.json` scripts and file structure before attempting to fix build errors. If both are present, determine the correct one and remove the other.
## 2026-01-05 - Testing Infrastructure

**Learning:** The frontend lacked essential testing libraries (`@testing-library/jest-dom`, `jest-mock-axios`) and configuration (mocking `IntersectionObserver`, `axios`, and wrapping App in `Redux Provider`). These are foundational for running any meaningful tests in this stack.

**Action:** When setting up or fixing a React test environment, immediately check for and install these core testing dependencies and ensure global mocks are present in `setupTests.js`.
