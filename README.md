# Agri B2B E-Commerce Platform

A production-ready Django E-Commerce site for Agriculture B2B.

## Setup

1.  **Install Dependencies:**

    ```bash
    pip install django pillow
    ```

2.  **Run Migrations:**

    ```bash
    python manage.py migrate
    ```

3.  **Populate Data:**

    ```bash
    python populate_db.py
    ```

4.  **Run Server:**

    ```bash
    python manage.py runserver
    ```

5.  **Access:**
    Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Features implemented

- **Models**: Vendor, Product, Category
- **Views**: Frontpage with dynamic data
- **Templates**: Premium design with Bootstrap 5
- **Assets**: Generated hero background and placeholders
