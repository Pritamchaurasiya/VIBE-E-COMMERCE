
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from store.models import Product, Category, Vendor, ProductImage, Review
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext

@pytest.mark.django_db
def test_product_list_nplusone():
    # Setup data
    category = Category.objects.create(name="Test Category", slug="test-category")
    user = User.objects.create_user(username="vendor", password="password")
    vendor = Vendor.objects.create(name="Test Vendor", slug="test-vendor", created_by=user)

    # Create 5 products
    for i in range(5):
        product = Product.objects.create(
            name=f"Product {i}",
            slug=f"product-{i}",
            category=category,
            vendor=vendor,
            price=100,
            stock_quantity=10,
            is_active=True
        )
        # Add 2 images per product
        ProductImage.objects.create(product=product, image="img1.jpg")
        ProductImage.objects.create(product=product, image="img2.jpg")

        # Add 2 reviews per product
        reviewer1 = User.objects.create_user(username=f"user{i}_1", password="password")
        Review.objects.create(product=product, user=reviewer1, rating=5, comment="Nice")

        reviewer2 = User.objects.create_user(username=f"user{i}_2", password="password")
        Review.objects.create(product=product, user=reviewer2, rating=4, comment="Good")

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse('api_products')

    # Warm up queries (if any setup needed)
    with connection.cursor() as cursor: # Ensure context
        pass

    # Execute request and count queries
    with CaptureQueriesContext(connection) as ctx:
        response = client.get(url)

    query_count = len(ctx.captured_queries)
    print(f"\nNumber of queries: {query_count}")

    # Analyze queries
    for q in ctx.captured_queries:
        print(f"QUERY: {q['sql'][:100]}...")

    assert response.status_code == 200

    # Expected: 1 (list) + 5 (images) + 5 (reviews for avg) + 5 (reviews for count) = 16 queries or more?
    # Serializer calls:
    # get_images -> obj.images.all() -> 1 query per product
    # get_average_rating -> obj.reviews.aggregate -> 1 query per product
    # get_review_count -> obj.reviews.count() -> 1 query per product

    # With 5 products: 1 main + 5 images + 5 avg + 5 count = 16 queries.
    # Ideally should be constant (around 2-3 queries).

    assert query_count < 10, f"Too many queries: {query_count}"
