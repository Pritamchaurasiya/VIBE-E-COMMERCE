import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from django.contrib.auth.models import User
from store.models import Product, Wishlist, Category, Vendor
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.urls import reverse

@pytest.mark.django_db
def test_product_list_wishlist_performance():
    # Setup
    client = APIClient()
    user = baker.make(User)
    client.force_authenticate(user=user)

    # Create required relations
    category = baker.make(Category)
    vendor = baker.make(Vendor)

    # Create 20 products
    products = baker.make(
        Product,
        _quantity=20,
        is_active=True,
        stock_quantity=10,
        category=category,
        vendor=vendor
    )

    # Add first 5 to wishlist
    for p in products[:5]:
        Wishlist.objects.create(user=user, product=p)

    url = reverse('api_products')

    # Warm up / check correctness
    response = client.get(url)
    assert response.status_code == 200

    # Check that is_in_wishlist is correct
    data = response.data['results'] if 'results' in response.data else response.data
    # data might be paginated or list depending on view config.
    # ProductListView uses pagination.

    if isinstance(data, list):
        # Check first product (which is in wishlist)
        # Note: ordering might differ, let's find one we added
        wishlist_ids = [p.id for p in products[:5]]
        for item in data:
            if item['id'] in wishlist_ids:
                assert item['is_in_wishlist'] is True
            else:
                assert item['is_in_wishlist'] is False

    # Measure queries
    with CaptureQueriesContext(connection) as ctx:
        client.get(url)

    query_count = len(ctx.captured_queries)
    print(f"\nCaptured Queries: {query_count}")

    # Before optimization:
    # 1 (Auth) + 1 (Count) + 1 (List products) + 20 (Wishlist checks) = ~23 queries
    # After optimization:
    # 1 (Auth) + 1 (Wishlist prefetch) + 1 (Count) + 1 (List products) = ~4 queries

    # Assert query count is low (optimized)
    # The exact number depends on auth and pagination overhead, but should be well below 10 for 20 items.
    assert query_count < 10
