# Master Prompt & Future Roadmap

## Project Overview
VIBE E-Commerce is a comprehensive platform for agricultural products, enabling B2B transactions between farmers, vendors, and retailers. It emphasizes performance, security, and user experience.

## Future Feature Roadmap (Next 4+ Features)

1.  **AI-Powered Personalization Engine**
    *   **Goal:** Increase conversion rates by showing relevant products.
    *   **Implementation:** Leverage `UserInteraction` and `AnalyticsEvent` data. Implement collaborative filtering or content-based recommendation algorithms (using `scikit-learn` or external API) to populate `PersonalizedRecommendationsView`.
    *   **UI:** "Recommended for You" sections on homepage and product details.

2.  **Advanced Inventory Management System**
    *   **Goal:** Support complex B2B logistics.
    *   **Implementation:** Add support for multi-warehouse inventory, batch tracking (for expiry dates), and low-stock predictive alerts.
    *   **UI:** Vendor dashboard for inventory insights and bulk updates.

3.  **B2B Negotiation & RFQ System**
    *   **Goal:** Facilitate large-volume deals.
    *   **Implementation:** Enhance the `RFQ` and `BulkOrder` models. Create a real-time chat interface (using Django Channels) for buyers and sellers to negotiate prices and terms. Auto-generate contracts/invoices upon agreement.
    *   **UI:** "Request Quote" button, Negotiation Chatbox, Offer/Counter-offer interface.

4.  **Integrated Logistics & Shipment Tracking**
    *   **Goal:** Provide end-to-end visibility.
    *   **Implementation:** Integrate with 3rd party logistics APIs (e.g., Shiprocket, Delhivery). Webhooks to update `Order` status automatically.
    *   **UI:** Real-time shipment tracking timeline in User Order History.

## Technical Enhancements

*   **Frontend Migration:** Transition `frontend` from Create React App to Next.js for better SEO (SSR/ISR) and performance (as per `frontend/NEXT_JS_MIGRATION_GUIDE.md`).
*   **Test Suite Reliability:** Fix authentication dependencies in tests (mocking permissions or creating proper test users). Address `django-csp` and `Axes` configuration in test environment.
*   **API Documentation:** Ensure all new endpoints are documented with Swagger/OpenAPI (`drf-yasg`).

## Operational Guidelines for AI Agents

*   **Performance First:** Always measure query counts and response times. Use `select_related`, `prefetch_related`, and database indexes.
*   **Security:** Follow `SecurityTrackingMiddleware` patterns. Validate inputs using `InputValidator`.
*   **Code Quality:** Run linting and tests before submission. Keep changes atomic.
