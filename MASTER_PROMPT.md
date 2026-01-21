# MASTER PROMPT: Future Features & Roadmap

This document outlines the next 4 major features to be implemented in the VIBE E-Commerce project, along with a roadmap for continuous improvement.

## 🚀 Future Features (Master Prompt)

### 1. Real-time Order Tracking (WebSockets)
**Goal:** Provide users with live updates on their order status (Processing -> Shipped -> Out for Delivery -> Delivered) without refreshing the page.
**Implementation:**
*   Use `Django Channels` and `Redis` for WebSocket connections.
*   Create a `OrderConsumer` to push status updates.
*   Frontend: Integrate `WebSocket` API to listen for order events and update the UI in real-time.
*   Add a map view for "Out for Delivery" using a mock driver location service.

### 2. Advanced Search with ElasticSearch
**Goal:** Replace the basic database-backed search with a powerful, typo-tolerant, and faceted search engine.
**Implementation:**
*   Integrate `ElasticSearch` or `Whoosh`.
*   Index Products, Categories, and Vendors.
*   Implement "Fuzzy Search" (handle typos).
*   Add faceted filtering (filter by brand, price range, rating, color, size) with instant counts.

### 3. Social Login & Multi-Factor Authentication (MFA)
**Goal:** Simplify user onboarding and enhance account security.
**Implementation:**
*   Use `django-allauth` for Google/Facebook/GitHub login.
*   Implement TOTP-based MFA (Time-based One-Time Password) using Google Authenticator for admin and high-value accounts.
*   Add "Login with OTP" (SMS/Email) as a passwordless option.

### 4. Progressive Web App (PWA) Offline Capabilities
**Goal:** Allow users to browse products and view their cart even when offline.
**Implementation:**
*   Enhance `serviceWorker.js` to cache API responses (product lists) and static assets.
*   Implement "Background Sync" to queue actions (like "Add to Cart") while offline and sync when online.
*   Add "Add to Home Screen" prompt for mobile users.

---

## 🛠️ Continuous Improvement Plan

### Backend
*   **Performance:** Optimize database queries using `select_related` and `prefetch_related` in all new views. Use `django-debug-toolbar` to identify bottlenecks.
*   **Security:** Regularly rotate `SECRET_KEY` and API keys. Enforce stricter rate limiting on sensitive endpoints (Login, Payment).
*   **Testing:** Maintain high test coverage (>80%). Add integration tests for critical flows (Checkout, Payment).

### Frontend
*   **Accessibility:** Ensure all new components meet WCAG 2.1 AA standards (keyboard navigation, ARIA labels).
*   **Performance:** Implement code splitting and lazy loading for all heavy components. Optimize images using WebP format.
*   **UX:** Standardize error handling and loading states across the application.

## 📝 Fixes & Enhancements Executed

*   **Fixed Race Condition:** `CouponService` now uses atomic `F()` expressions to prevent race conditions during coupon application.
*   **Fixed Security Vulnerability:** `ApplyCouponView` now calculates the cart total server-side, ignoring potentially manipulated client input.
*   **Enhanced Security:** Added `AnonRateThrottle` to Flash Sale API endpoints to prevent abuse.
