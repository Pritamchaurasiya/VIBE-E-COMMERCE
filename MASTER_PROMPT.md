# Agri-Tech B2B Platform - Roadmap & Enhancement Plan

## Project Overview
This project is a comprehensive B2B/B2C marketplace for agricultural products (seeds, fertilizers, tools) with advanced analytics, tracking, and vendor management. It aims to empower farmers and retailers with technology.

## Completed & Working Features
*   **E-commerce Core:** Product listing, search, cart, checkout, payments (Stripe/COD), order management.
*   **Vendor System:** Vendor profiles, inventory management, analytics dashboard.
*   **Tracking & Security:** Detailed user tracking, admin alerts, file operation monitoring, security headers.
*   **Analytics:** User behavior tracking, sales analytics, database monitoring.
*   **PWA Support:** Offline capabilities, install prompts (in progress).
*   **Agri-Specifics:** Crop and Disease models, "Shop by Crop".

## Upcoming Features (The "Master Prompt" Roadmap)

### 1. AI Crop Doctor (Image Diagnosis)
*   **Concept:** Farmers can upload photos of sick plants. An AI model (TensorFlow/PyTorch) analyzes the image to detect diseases (e.g., Late Blight, Rust).
*   **Integration:**
    *   **Frontend:** Camera capture UI, image upload.
    *   **Backend:** API endpoint to receive image, pass to ML model, return diagnosis + **Recommended Products** from the store that treat that disease.
    *   **Data:** Utilize the existing `Disease` and `ProductDiseaseMapping` models.

### 2. Real-Time Mandi Prices (Market Integration)
*   **Concept:** Display daily market prices (APMC) for various crops in different regions/states.
*   **Integration:**
    *   **Backend:** A scheduled task (Celery) to scrape or fetch data from government APIs (e.g., eNAM or data.gov.in).
    *   **Frontend:** A "Market Prices" ticker or dashboard page allowing filtering by state/crop.
    *   **Alerts:** Users can set price alerts for specific crops.

### 3. Soil Health Card Digitization & Recommendations
*   **Concept:** Farmers input parameters from their physical Soil Health Card (N, P, K values, pH, EC).
*   **Logic:** The system calculates nutrient deficiencies and automatically recommends the correct fertilizer mix and quantity.
*   **Enhancement:** Save historical soil data to track improvement over time.

### 4. Rent-a-Tool (Farming as a Service - FaaS)
*   **Concept:** Allow vendors (or other farmers) to list heavy machinery (tractors, drones, harvesters) for *rent* by the hour/day, not just for sale.
*   **Technical:**
    *   **New Models:** `RentalEquipment`, `RentalBooking`, `BookingCalendar`.
    *   **Frontend:** Booking interface with date selection.
    *   **Logic:** Availability checking, deposit handling.

### 5. Kisan Charcha (Community Forum)
*   **Concept:** A Q&A and discussion forum for farmers to share knowledge and ask experts.
*   **Features:**
    *   Tags (by crop, season).
    *   Upvoting/Helpful markers.
    *   Expert badges for verified agronomists.
    *   Voice-to-text support for accessibility.

### 6. Voice Commerce & Multilingual Support
*   **Concept:** Make the app accessible to non-tech-savvy users.
*   **Voice:** "Search for urea" -> App searches.
*   **Language:** Full translation (i18n) into Hindi, Marathi, Telugu, etc. (Infrastructure already present in `settings.py`, needs frontend implementation).

## Enhancement & Fixes Log
*   **Frontend:** Fixed broken API imports (`getAnalyticsDashboard`), removed conflicting `next` dependency, installed missing UI/Logic libraries (`lucide-react`, `redux`).
*   **Backend:** Installed missing dependencies (`django-axes`, `stripe`, etc.), fixed `settings.py` authentication backend warning, verified migrations for new tracking/agri models.
*   **Security:** Enhanced authentication backends with `axes` for brute-force protection.
