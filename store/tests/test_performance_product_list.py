
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.test import override_settings
from store.models import Product, Category, Vendor, Review, ProductImage, User
from django.db import reset_queries


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}},
    MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ],
)
class TestProductListPerformance(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("api_products")

        # Create common objects
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )
        self.vendor = Vendor.objects.create(
            name="Test Vendor", slug="test-vendor", city="Test City"
        )
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.force_authenticate(user=self.user)

    def create_products(self, count):
        products = []
        for i in range(count):
            product = Product.objects.create(
                name=f"Product {i}",
                slug=f"product-{i}",
                category=self.category,
                vendor=self.vendor,
                price=100.00,
                stock_quantity=10,
                is_active=True,
            )
            # Add images
            ProductImage.objects.create(product=product, image="products/test.jpg")
            ProductImage.objects.create(product=product, image="products/test2.jpg")

            # Add reviews
            Review.objects.create(
                product=product, user=self.user, rating=5, comment="Great!"
            )
            # Create another user for second review
            user2 = User.objects.create_user(username=f"user{i}", password="password")
            Review.objects.create(
                product=product, user=user2, rating=4, comment="Good"
            )

            products.append(product)
        return products

    def test_product_list_queries(self):
        # Create 10 products
        self.create_products(10)

        # Clear existing queries
        reset_queries()

        # Make request and count queries
        # 1. Count query for pagination
        # 2. Main query for products (with annotations)
        # 3. Prefetch query for images
        with self.assertNumQueries(3):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
