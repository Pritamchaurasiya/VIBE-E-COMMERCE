# VIBE E-Commerce - Master Prompt & Roadmap

This document serves as the central context and roadmap for the VIBE E-Commerce Agri-B2B project. It outlines the current state, technical architecture, and the strategic roadmap for future development. Future agents should consult this file to understand the project's direction.

---

## 🏗️ Project Status (Current State)

**Status:** Production-Ready (Polished & Secure)
**Last Updated:** December 2024

The project is a fully functional B2B e-commerce platform tailored for the agricultural sector. It includes:
-   **Backend:** Django 5.1+ (downgraded from 6.0 for compatibility) with DRF. Secure, scalable, and modular.
    -   *Key Fixes:* Consolidated tracking models in `store/tracking_models.py`, fixed `requirements.txt` dependency conflicts, updated CSP settings.
-   **Frontend:** React 18 with Material UI. Responsive and accessible.
    -   *Key Fixes:* Resolved `axios` ESM compatibility issues in tests.
-   **Features:**
    -   Multi-vendor marketplace.
    -   Advanced tracking & analytics (User behavior, System access, File ops).
    -   Agri-specific features (Crop mapping, Bulk pricing).
    -   Secure authentication (JWT, Axes brute-force protection).

---

## 🚀 Future Roadmap: 4+ Strategic Features

The following features are prioritized to enhance the value proposition for farmers and agri-businesses:

### 1. 🌾 AI-Powered Crop Disease Diagnosis (Vision API)
**Goal:** Empower farmers to diagnose crop issues instantly using their phone camera.
-   **Implementation:**
    -   Integrate a custom ML model (TensorFlow/PyTorch) or API (e.g., Google Vision/Azure Custom Vision).
    -   Frontend: Camera capture component with offline support.
    -   Backend: Async processing (Celery) to analyze images and return diagnosis + product recommendations from the catalog.

### 2. 🔗 Blockchain-Based Supply Chain Transparency
**Goal:** Build trust by proving the origin and quality of seeds/fertilizers.
-   **Implementation:**
    -   Store critical transaction hashes (Batch #, Origin, Certification) on a private/public ledger (e.g., Hyperledger or Polygon).
    -   Generate QR codes for product packaging that buyers can scan to view the full journey.

### 3. 🎙️ Vernacular Voice-Activated Shopping Assistant
**Goal:** Make the platform accessible to farmers with lower literacy or language barriers.
-   **Implementation:**
    -   Integrate Web Speech API or Azure Speech Services.
    -   Support for key Indian languages (Hindi, Telugu, Tamil, etc.).
    -   "Speak to Search" and "Voice Checkout" flows.

### 4. 📶 Offline-First Mobile Experience (PWA 2.0)
**Goal:** Ensure functionality in remote areas with spotty internet.
-   **Implementation:**
    -   Enhance Service Workers (Workbox) to cache the entire product catalog and user cart.
    -   Background Sync API to queue orders and sync when online.
    -   LocalForage/IndexedDB for robust client-side storage of heavy assets.

### 5. 📡 IoT Sensor Integration Dashboard
**Goal:** Connect with smart farming devices.
-   **Implementation:**
    -   MQTT broker integration to receive data from soil moisture/pH sensors.
    -   Dashboard to visualize real-time farm health.
    -   Automated product recommendations based on sensor alerts (e.g., "Low Nitrogen" -> Recommend Urea).

---

## 🤖 Instructions for Future Agents

1.  **Context Loading:** Always read `store/tracking_models.py` and `store/models.py` to understand the data structure. The tracking models have been refactored into their own file.
2.  **Testing:** Run `pnpm test` in the `frontend` directory to verify UI changes. Run `python manage.py check` for backend integrity.
3.  **Dependencies:** Strict adherence to `requirements.txt` (Django < 6.0) and `frontend/package.json`. Do not upgrade Django to 6.0+ without resolving `django-celery-beat` conflicts.
4.  **Security:** Maintain CSP compliance. Any new external script/style source must be added to `CONTENT_SECURITY_POLICY` in `config/settings.py`.

---

**Mission:** To build the most robust, accessible, and intelligent Agri-B2B platform in the world.
