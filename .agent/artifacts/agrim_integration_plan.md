# AGRIM-Style Agri B2B Platform Integration Plan

## Overview

Transform the existing VIBE-E-COMMERCE into a mobile-first, AGRIM-inspired Agri B2B marketplace with rural-optimized features.

---

## 🎨 DESIGN SYSTEM

### Color Palette (Agricultural Theme)

```css
:root {
  /* Primary Colors */
  --agri-green-primary: #2e7d32; /* Forest Green - Main brand */
  --agri-green-light: #4caf50; /* Leaf Green - Success states */
  --agri-green-dark: #1b5e20; /* Deep Green - Headers */

  /* Secondary Colors */
  --agri-brown: #795548; /* Earth Brown - Accents */
  --agri-yellow: #ffc107; /* Harvest Gold - Highlights */
  --agri-orange: #ff9800; /* Sunset Orange - Deals/Offers */

  /* Neutral Colors */
  --agri-cream: #fff8e1; /* Cream - Backgrounds */
  --agri-soil: #3e2723; /* Dark Soil - Text */
  --agri-sand: #efebe9; /* Sand - Cards */

  /* Functional Colors */
  --discount-red: #e53935; /* Price cuts */
  --trend-up: #43a047; /* Price increase */
  --trend-down: #e53935; /* Price decrease */
}
```

### Typography

- **Headings**: Inter/Poppins (Bold)
- **Body**: Roboto/Open Sans
- **Hindi Support**: Noto Sans Devanagari

---

## 📱 FRONTEND COMPONENTS

### 1. Top Navigation Bar

```text
┌─────────────────────────────────────────────────┐
│ 🌾 AGRI-VIBE   [🔍 Search products...]  🔔(3) 🛒 │
└─────────────────────────────────────────────────┘
```

- **Search**: Autocomplete with product suggestions, recent searches
- **Notifications**: Badge with unread count
- **Cart**: Floating count badge

### 2. Homepage Sections (Scroll Order)

| Section              | Priority | Description                           |
| -------------------- | -------- | ------------------------------------- |
| Promo Banner         | 1        | Carousel: "Get ₹400 off with APP400"  |
| Deal of the Day      | 2        | Timer + featured products             |
| Recently Viewed      | 3        | Products with price trend arrows      |
| Popular in [City]    | 4        | Location-based suggestions            |
| Shop by Category     | 5        | Seeds, Fertilizers, Tools, Pesticides |
| Shop by Crop         | 6        | Visual crop icons grid                |
| Shop by Disease      | 7        | Leaf Miner, Powdery Mildew, etc.      |
| High Margin Products | 8        | Retailer-focused section              |
| Newly Launched       | 9        | Latest additions                      |
| Shop by Brand        | 10       | Brand logo carousel                   |

### 3. Product Card Design

```text
┌──────────────────────────┐
│  [INSTANT PACK]  ❤️      │
│  ┌────────────────┐      │
│  │   Product      │      │
│  │   Image        │      │
│  └────────────────┘      │
│  Product Name            │
│  500ml | 1L | 5L         │
│  ₹̶4̶5̶0̶  ₹380  (15% OFF)  │
│  Bulk: ₹350/unit (10+)   │
│  [  + Add to Cart  ]     │
└──────────────────────────┘
```

### 4. Bottom Navigation

```text
┌─────────────────────────────────────────────┐
│  🏠 Home  |  🏪 Store  |  💳 Credit  |  🎁 Offers  |  👤 Account  │
└─────────────────────────────────────────────┘
```

---

## 🔧 BACKEND MODULES

### Module 1: Enhanced User System

```python
# New Models
- UserProfile (extended)
  - role: [retailer, distributor, farmer]
  - business_name, pan_number, gst_number
  - location (city, district, state, pincode)
  - coin_balance, credit_limit
  - kyc_status, kyc_documents

- OTPVerification
  - phone, otp, expires_at, verified
```

### Module 2: Product Catalog Enhancement

```python
# Enhanced Product Model
- Product (extended)
  - packing_options: JSONField  # [{size: "500ml", price: 380}, ...]
  - bulk_pricing: JSONField     # [{min_qty: 10, price: 350}, ...]
  - is_instant_pack: Boolean
  - margin_percentage: Decimal
  - launch_date: Date
  - trending_score: Integer

# New Models
- Crop (name, image, slug)
- Disease (name, image, symptoms)
- ProductCropMapping (M2M)
- ProductDiseaseMapping (M2M)
```

### Module 3: Location-Based Engine

```python
# Models
- LocationPopularity
  - city, product, view_count, purchase_count

# Features
- Auto-detect location via IP/GPS
- City-wise trending products
- Regional pricing support
```

### Module 4: Discount & Promo Engine

```python
# Enhanced Coupon Model
- Coupon (extended)
  - code_type: [flat, percentage, bulk, first_order]
  - min_cart_value, max_discount
  - applicable_categories, applicable_products
  - user_usage_limit, total_usage_limit

# New Models
- PriceAlert
  - user, product, target_price, is_active
```

### Module 5: Notification System

```python
# Models
- Notification
  - user, title, message, type
  - is_read, created_at
  - action_url, image_url

# Types: price_drop, new_launch, order_update, promo, system
```

---

## 📁 FILE STRUCTURE

```text
frontend/src/
├── components/
│   ├── layout/
│   │   ├── TopNav.js           # AGRIM-style search bar
│   │   ├── BottomNav.js        # 5-tab mobile nav
│   │   └── MobileLayout.js     # Wrapper component
│   ├── home/
│   │   ├── PromoBanner.js      # Carousel banners
│   │   ├── DealOfDay.js        # Timer + products
│   │   ├── RecentlyViewed.js   # With price trends
│   │   ├── PopularInCity.js    # Location-based
│   │   ├── ShopByCategory.js   # Category grid
│   │   ├── ShopByCrop.js       # Crop icons
│   │   ├── ShopByDisease.js    # Disease cards
│   │   ├── HighMargin.js       # Margin products
│   │   ├── NewlyLaunched.js    # New products
│   │   └── ShopByBrand.js      # Brand logos
│   ├── products/
│   │   ├── AgriProductCard.js  # AGRIM-style card
│   │   ├── PackingOptions.js   # Size selector
│   │   └── PriceTrend.js       # ↑↓ indicator
│   ├── account/
│   │   ├── BusinessProfile.js
│   │   ├── CoinBalance.js
│   │   └── OrderHistory.js
│   └── common/
│       ├── SearchAutocomplete.js
│       ├── NotificationBell.js
│       └── OfflineBanner.js
├── pages/
│   ├── AgriHome.js
│   ├── StorePage.js
│   ├── CreditPage.js
│   ├── OffersPage.js
│   └── AccountPage.js
├── styles/
│   └── agri-theme.css
└── utils/
    ├── locationService.js
    └── offlineStorage.js
```

---

## 🚀 IMPLEMENTATION PHASES

### Phase 1: Core UI (Week 1-2)

- [x] Design system & theme CSS
- [ ] TopNav with search
- [ ] BottomNav (5 tabs)
- [ ] Homepage sections skeleton
- [ ] AgriProductCard component

### Phase 2: Homepage Sections (Week 2-3)

- [ ] Promo Banner carousel
- [ ] Deal of the Day with timer
- [ ] Recently Viewed with trends
- [ ] Shop by Category/Crop/Disease
- [ ] Brand showcase

### Phase 3: Backend Enhancements (Week 3-4)

- [ ] Extended User/Profile model
- [ ] Product enhancements (packing, bulk pricing)
- [ ] Location popularity tracking
- [ ] Notification system
- [ ] Promo engine upgrade

### Phase 4: Mobile Optimization (Week 4-5)

- [ ] PWA setup (offline support)
- [ ] Touch gestures
- [ ] Low-bandwidth image loading
- [ ] Hindi language support

---

## 📊 API ENDPOINTS (New/Modified)

```text
# Location
GET  /api/v1/location/popular/{city}/     # Popular in city
GET  /api/v1/location/detect/             # Auto-detect location

# Products (Enhanced)
GET  /api/v1/products/deal-of-day/        # Deal of the day
GET  /api/v1/products/high-margin/        # High margin products
GET  /api/v1/products/newly-launched/     # New arrivals
GET  /api/v1/products/by-crop/{crop_id}/  # Products for crop
GET  /api/v1/products/by-disease/{id}/    # Products for disease

# User (Enhanced)
POST /api/v1/auth/otp/send/               # Send OTP
POST /api/v1/auth/otp/verify/             # Verify OTP
GET  /api/v1/profile/coins/               # Coin balance
GET  /api/v1/profile/credit-limit/        # Credit info

# Notifications
GET  /api/v1/notifications/               # All notifications
POST /api/v1/notifications/mark-read/     # Mark as read
GET  /api/v1/notifications/unread-count/  # Badge count

# Offers
GET  /api/v1/offers/active/               # Active promos
POST /api/v1/offers/apply/                # Apply promo code
```

---

## 🌐 OFFLINE SUPPORT STRATEGY

1. **Service Worker**: Cache static assets, API responses
2. **IndexedDB**: Store cart, recent products locally
3. **Sync Queue**: Queue actions when offline, sync when online
4. **Low-Res Images**: Serve compressed images for slow networks
5. **Skeleton Loading**: Show placeholders during load

---

## ✅ SUCCESS METRICS

- Mobile page load < 3s on 3G
- Offline functionality for cart/browsing
- 100% responsive across devices
- Hindi language support
- Location-based personalization active
