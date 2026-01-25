# Master Project Prompt & Roadmap

This document serves as the master guide for the project's future development, ensuring continuity and focus on high-impact features and quality.

## Project Vision
To build the most accessible, intuitive, and robust agricultural B2B platform ("Agri-Vibe") that empowers farmers and vendors with seamless technology.

## Core Directives for Future Agents
1.  **Backend & Frontend Harmony**: Always ensure that backend API changes (serializers, views) are synchronized with frontend consumption. verify types and data structures.
2.  **Zero-Regression Policy**: Run tests (`pnpm test`, `pytest`) before every submission. Fix what you break.
3.  **Accessibility First**: Every new UI component must be keyboard accessible and screen-reader friendly. Use "Palette's" standards.
4.  **Performance**: Optimize queries (N+1 prevention) and frontend bundles.

## Future Roadmap (Next 4+ Features)

### 1. 🎤 Voice Search Integration
*   **Goal**: Allow farmers to search for products using voice commands (Hindi/English).
*   **Implementation**: Enhance `SearchAutocomplete.js` with Web Speech API.
*   **UX**: Add a microphone icon. On click, listen and populate the search bar. Show "Listening..." state.

### 2. 📶 Robust Offline Mode
*   **Goal**: Enable browsing and cart actions in low-connectivity areas.
*   **Implementation**: specific service worker caching strategies (Workbox) for product lists and static assets. Queue cart actions using `background-sync`.
*   **UX**: "You are offline" banner (already referenced in CSS) should be functional.

### 3. 🌐 Multi-language Support (i18n)
*   **Goal**: Support Hindi, Marathi, and Punjabi for broader accessibility.
*   **Implementation**: Use `i18next`. Create JSON translation files. Add a language switcher in the `Header`.
*   **UX**: Ensure UI handles variable text lengths without breaking layout.

### 4. 🍂 AI Crop Disease Detection
*   **Goal**: Users upload a leaf photo, system identifies disease and recommends products.
*   **Implementation**: New endpoint `/api/v1/detect-disease/`. Frontend upload component with preview.
*   **UX**: Simple "Take Photo" interface. clear confidence score and "Treat with..." product links.

### 5. 🚜 Machinery Rental Marketplace
*   **Goal**: Allow vendors to list tractors/harvesters for rent.
*   **Implementation**: New `Rental` model and booking system.
*   **UX**: Calendar based availability picker.

## Current Maintenance Focus
*   **Security**: Regular audit of `sanitize_for_csv` and API permissions.
*   **Stability**: Fix the `axios` vs `jest` compatibility issue in frontend tests.
*   **Consistency**: Standardize currency formatting (`₹`) across all components.

---
*Maintained by the Agent Collective.*
