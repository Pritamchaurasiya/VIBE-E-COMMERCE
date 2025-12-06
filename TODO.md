# Project Audit and Todo List

## Completed Improvements

- [x] **Frontend Integration**:
  - Connected Wishlist buttons to backend via AJAX.
  - Connected "Add to Cart" to backend via AJAX with animations.
  - Implemented Dark/Light mode toggle with persistence.
  - Fixed template syntax errors (nested `if` tags).
  - Refactored JS to remove deep nesting (`handleAddToCartSubmit`).
  - Added responsive styles for carousel.

## Backend Audit Findings

- **Models**:
  - `Vendor.created_by` uses `CASCADE` delete. Consider `SET_NULL` or `PROTECT` for data safety in future.
  - `Product` includes Agri-specific fields (`technical_name`, `target_crops`).
  - `Order` supports partial payment logic (`paid_amount`).
- **Views**:
  - `start_order` endpoint lacks `@require_POST` decorator.
  - `cart` endpoints lack `@require_POST` decorator for state-changing actions.
  - Price filtering in `shop` view swallows `ValueError` without feedback (acceptable for now, but could be cleaner).
- **Security**:
  - CSRF protection is active (relies on frontend token).
  - API endpoints use `json.loads` without strict schema validation (acceptable for MVP).

## Upcoming Tasks

- [ ] **Refactoring**:
  - Add `@require_POST` to mutation views (`start_order`, `cart_add`, `wishlist_add`, etc.) in `store/views.py`.
  - Improve `cart_update` to handle arbitrary quantities if needed (currently +/- 1).
- [ ] **Testing**:
  - Verify Stripe integration with real test keys.
  - Test mobile responsiveness on actual devices.
- [ ] **Features**:
  - Implement "Forgot Password" flow.
  - Add email notifications for Order Confirmation.
  - Implement Vendor Dashboard for product management.
