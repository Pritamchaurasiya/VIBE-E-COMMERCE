# VIBE E-Commerce - Agri B2B Platform

A full-stack e-commerce platform for agricultural products, built with Django backend and React frontend. Features include product listings, vendor management, flash sales, bulk ordering, and more.

## 🌟 Features

### Core E-Commerce

- **Product Catalog**: 100+ products with categories, images, and detailed descriptions
- **Vendor System**: Multi-vendor marketplace with vendor dashboards
- **Shopping Cart**: Session-based cart with quantity management
- **Order Management**: Complete order flow with status tracking
- **Reviews & Ratings**: Product reviews with verified purchase badges

### Advanced Features

- **Flash Sales**: Time-limited deals with countdown timers
- **Bulk Ordering**: Special pricing for bulk purchases
- **Crop/Disease Mapping**: Products linked to specific crops and diseases (Agri-specific)
- **Deal of the Day**: Daily featured products with discounts
- **Price Alerts**: Notify users when prices drop
- **User Coins**: Loyalty reward system

### Security (OWASP Compliant)

- Rate limiting on authentication endpoints
- Input sanitization with bleach
- CSRF protection
- Secure session management
- XSS prevention
- SQL injection protection via Django ORM

## 🛠 Tech Stack

### Backend

- **Framework**: Django 5.2
- **API**: Django REST Framework
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Authentication**: Token-based + Session
- **Caching**: Local Memory / Redis (optional)

### Frontend

- **Framework**: React 18
- **UI Library**: Material UI
- **State Management**: React Context
- **HTTP Client**: Axios
- **Animations**: Framer Motion

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- pip and npm

### Backend Setup

```bash
# Clone the repository
git clone <repository-url>
cd VIBE-E-COMMERCE

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Populate database with sample data
python populate_db.py
python add_reviews.py

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 📁 Project Structure

```text
VIBE-E-COMMERCE/
├── config/              # Django settings and configuration
├── store/               # Main Django app
│   ├── api_views.py     # REST API endpoints
│   ├── views.py         # Template views
│   ├── models.py        # Database models
│   ├── serializers.py   # DRF serializers
│   ├── forms.py         # Django forms
│   └── tests/           # Test suite
├── templates/           # HTML templates
├── static/              # Static files
├── media/               # User uploads
├── frontend/            # React application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API services
│   │   └── App.js       # Main app component
│   └── package.json
├── manage.py
├── requirements.txt
└── README.md
```

## 🔐 Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable                     | Description       | Required     |
| ---------------------------- | ----------------- | ------------ |
| `SECRET_KEY`                 | Django secret key | Yes          |
| `DEBUG`                      | Enable debug mode | Yes          |
| `STRIPE_API_KEY_PUBLISHABLE` | Stripe public key | For payments |
| `STRIPE_API_KEY_HIDDEN`      | Stripe secret key | For payments |
| `EMAIL_HOST_USER`            | SMTP email        | For emails   |
| `EMAIL_HOST_PASSWORD`        | SMTP password     | For emails   |

## 📡 API Endpoints

### Authentication

- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/logout/` - User logout

### Products

- `GET /api/v1/products/` - List products
- `GET /api/v1/products/<slug>/` - Product details
- `GET /api/v1/categories/` - List categories

### Cart & Orders

- `GET/POST /api/v1/cart/` - Cart operations
- `GET /api/v1/orders/` - User orders
- `POST /api/v1/apply-coupon/` - Apply coupon

### Vendors

- `GET /api/v1/vendors/` - List vendors
- `GET /api/v1/vendors/<slug>/` - Vendor details

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific test module
python manage.py test store.tests.test_models

# Run with coverage
coverage run manage.py test
coverage report
```

## 📦 Production Deployment

1. Set `DEBUG=False` in `.env`
2. Configure PostgreSQL database
3. Set up Redis for caching (optional)
4. Collect static files: `python manage.py collectstatic`
5. Use gunicorn or uwsgi as WSGI server
6. Set up nginx as reverse proxy

## 📝 License

This project is licensed under the MIT License.

## 👥 Contributors

- VIBE E-Commerce Team
