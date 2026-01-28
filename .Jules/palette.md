# Palette's Journal

## 2025-02-18 - Async Action States & Environment Stability

**Learning:** Instant feedback states (like "Added to cart") must effectively mask latency. Relying on boolean flags that don't differentiate between 'loading' and 'success' leads to misleading UX where the action appears complete before the server confirms it.
**Action:** Always implement a 3-state system (idle, loading, success) for async user actions, using a spinner for 'loading' and a confirmation for 'success'.

**Learning:** Broken backend dependencies (e.g., conflicting Django versions) can block frontend visual verification.
**Action:** Prioritize robust unit tests with mocked contexts (like `AgriProductCard.test.js`) to verify UX logic when the full environment is unstable.
