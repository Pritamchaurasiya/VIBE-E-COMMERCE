
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from store.models import Product, Category, Vendor
from django.test.utils import CaptureQueriesContext
from django.db import connection

@pytest.mark.django_db
def test_recommendations_performance():
    # Setup data
    category = Category.objects.create(name="Electronics", slug="electronics")
    vendor = Vendor.objects.create(name="TechStore", slug="techstore")

    main_product = Product.objects.create(
        name="Main Product",
        slug="main-product",
        category=category,
        vendor=vendor,
        price=100.00,
        stock_quantity=10,
        is_active=True
    )

    # Create related products to fill recommendations
    # 4 Same category
    for i in range(4):
        Product.objects.create(
            name=f"Cat Product {i}",
            slug=f"cat-product-{i}",
            category=category,
            vendor=vendor,
            price=200.00, # Different price to avoid price match
            stock_quantity=10,
            is_active=True
        )

    # 2 Same vendor (different category)
    other_category = Category.objects.create(name="Other", slug="other")
    for i in range(2):
        Product.objects.create(
            name=f"Vendor Product {i}",
            slug=f"vendor-product-{i}",
            category=other_category,
            vendor=vendor,
            price=200.00,
            stock_quantity=10,
            is_active=True
        )

    # 2 Similar price (different category, different vendor)
    other_vendor = Vendor.objects.create(name="OtherStore", slug="otherstore")
    for i in range(2):
        Product.objects.create(
            name=f"Price Product {i}",
            slug=f"price-product-{i}",
            category=other_category,
            vendor=other_vendor,
            price=100.00,
            stock_quantity=10,
            is_active=True
        )

    client = APIClient()
    # Use api_recommendations as per urls.py
    url = reverse('api_recommendations', args=[main_product.id])

    # Warmup
    client.get(url)

    # Measure
    with CaptureQueriesContext(connection) as ctx:
        # The view seems to require authentication based on error log, but usually recommendations should be public.
        # However, if it returns 401, we might need to authenticate or check permission_classes in the view.
        # Let's inspect RecommendationsView in store/api_views.py to see permission_classes.
        # If it uses default permissions, it might default to IsAuthenticated.
        # Assuming it needs to be public, but for now let's authenticate to bypass 401.

        # Actually, let's just make sure we can access it.
        # The view source:
        # class RecommendationsView(APIView):
        #     """API view for product recommendations."""
        #
        #     def get(self, _request, product_id):
        # ...
        # It inherits APIView which uses DEFAULT_PERMISSION_CLASSES from settings.
        # If settings say IsAuthenticated, then we need auth.

        from django.contrib.auth.models import User
        user = User.objects.create_user('testuser', 'test@example.com', 'password')
        client.force_authenticate(user=user)

        response = client.get(url)
        assert response.status_code == 200

    print(f"\nQueries count: {len(ctx.captured_queries)}")
    for query in ctx.captured_queries:
        print(query['sql'])
