from django.test import TestCase, override_settings
from django.db import connection
from django.test.utils import CaptureQueriesContext
from store.models import Product, Category, Vendor, ProductImage
from store.serializers import ProductSerializer
from store.api_views import ProductListView
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth.models import User

@override_settings(DEBUG=True)
class ProductPerformanceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.vendor = Vendor.objects.create(name="Test Vendor", slug="test-vendor", city="Test City")
        self.category = Category.objects.create(name="Test Category", slug="test-category")

        self.products = []
        for i in range(10):
            p = Product.objects.create(
                name=f"Product {i}",
                slug=f"product-{i}",
                price=100,
                category=self.category,
                vendor=self.vendor,
                stock_quantity=10,
                description="Test",
                is_active=True
            )
            ProductImage.objects.create(product=p, image="test.jpg")
            self.products.append(p)

    def test_product_list_queries(self):
        factory = APIRequestFactory()
        request = factory.get('/api/products/')
        force_authenticate(request, user=self.user)

        view = ProductListView.as_view()

        with CaptureQueriesContext(connection) as ctx:
            response = view(request)
            if hasattr(response, 'render'):
                response.render()

        print(f"\nResponse Status: {response.status_code}")

        query_count = len(ctx)
        print(f"DEBUG: Number of queries with 10 products: {query_count}")
        for i, q in enumerate(ctx.captured_queries):
            print(f"DEBUG Query {i}: {q['sql']}")

        self.assertEqual(response.status_code, 200)
        self.assertGreater(query_count, 0, "No queries were captured!")
