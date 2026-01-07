## 2026-01-07 - Inconsistent Currency Formatting and Missing Test Mocks
**Learning:** Found inconsistent currency symbols ('?' vs 'USD') and hardcoded placeholders. Standardizing via a utility function improves both visual consistency and code maintainability. Also, frontend tests were broken due to missing Redux wrappers and IntersectionObserver mocks.
**Action:** Always create a shared formatting utility for currency/dates. Ensure component tests are wrapped in necessary Providers (Redux, Theme, Auth) and browser APIs are mocked in setupTests.js.
