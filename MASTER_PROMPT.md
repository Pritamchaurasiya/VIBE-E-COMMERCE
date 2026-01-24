# MASTER PROMPT - VIBE E-Commerce (Agri B2B)

## Project Overview
VIBE E-Commerce is a specialized B2B platform for the agricultural sector. It connects farmers, retailers, and distributors with vendors of agricultural products (seeds, fertilizers, machinery, etc.). The platform emphasizes performance, accessibility (voice search, multi-language support), and agri-specific features (crop mapping, mandi prices, soil health).

## Tech Stack
- **Backend:** Django 5.2 (Python 3.10+), Django REST Framework, PostgreSQL (Prod) / SQLite (Dev)
- **Frontend:** React 18, Material UI, Framer Motion, Redux Toolkit
- **State Management:** React Context + Redux
- **Search:** ElasticSearch (Planned), Standard DB Search (Current)
- **Caching:** Redis (Optional), Local Memory

## Current Status
- **Core E-Commerce:** Product catalog, Cart, Checkout (Stripe/COD), Orders, Reviews.
- **Vendor System:** Vendor dashboards, inventory management.
- **Advanced Features:** Flash Sales, Bulk Orders, Recommendations.
- **Agri Features:** Shop by Crop, Shop by Disease.
- **Analytics:** Vendor Analytics, Admin Dashboard.

## Roadmap & Active Tasks

### Phase 1: Enhancement & Stability (Current Focus)
- [x] Fix Dependency Conflicts (Django Version)
- [x] **Voice Search Support:** Enable voice input for search (Accessibility).
- [x] **Weather Integration:** Real-time weather updates for farmers.
- [x] **Soil Health Cards:** Digital soil health reports and recommendations.
- [x] **Mandi/Market Prices:** Real-time market rates for crops.
- [x] **Master Prompt Creation:** This file.

### Phase 2: Advanced Intelligence
- [ ] AI-driven Pest Diagnosis (Image Upload).
- [ ] Predictive Analytics for Crop Yield.
- [ ] Multi-language Chatbot (Hindi/Regional).

### Phase 3: Scaling
- [ ] Microservices decomposition.
- [ ] Mobile App (React Native).

## Development Guidelines
1.  **Code Quality:** Follow PEP8 (Python) and ESLint (JS).
2.  **Testing:** All new backend features must have unit tests.
3.  **Security:** Use `bleach` for sanitization, enforce permissions.
4.  **Performance:** Avoid N+1 queries, use `select_related`/`prefetch_related`.
5.  **Accessibility:** Ensure ARIA labels and keyboard navigation.

## Repository Structure
- `config/`: Django settings.
- `store/`: Main Django app (Models, Views, APIs).
- `frontend/`: React application.
- `media/`: User uploads.
- `static/`: Static assets.

---
*Last Updated: 2024-05-22*
