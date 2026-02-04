import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from store.models import Product, Category, Vendor, Review
from django.contrib.auth.models import User
from django.test import override_settings
from django.db import connection, reset_queries

@pytest.mark.django_db
@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    DATABASE_ENGINE='sqlite'
)
def test_product_list_queries():
    # Setup
    user1 = User.objects.create_user(username='testuser1', password='password')
    user2 = User.objects.create_user(username='testuser2', password='password')
    category = Category.objects.create(name='Test Category', slug='test-category')
    vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

    # Create 5 products with reviews
    for i in range(5):
        p = Product.objects.create(
            name=f'Product {i}',
            slug=f'product-{i}',
            price=100,
            category=category,
            vendor=vendor
        )
        # Add reviews
        Review.objects.create(product=p, user=user1, rating=5, comment="Nice")
        Review.objects.create(product=p, user=user2, rating=4, comment="Good")

    client = APIClient()
    client.force_authenticate(user=user1)
    url = reverse('api_products')

    # Warmup
    client.get(url)

    # Debug=True is required for connection.queries to be populated
    with override_settings(DEBUG=True):
        reset_queries()
        response = client.get(url)
        queries = len(connection.queries)

        print(f"\nQueries count: {queries}")

        # After optimization:
        # 1. Main products list (with annotations)
        # 2. Count for pagination
        # 3. Images prefetch (1 query)
        # Total should be around 3.
        # We assert <= 5 to be safe against minor internal auth/session queries.

        assert queries <= 5
        assert response.status_code == 200
