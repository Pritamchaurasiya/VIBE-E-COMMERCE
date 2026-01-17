from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from store.models import Product, Category, Vendor, Wishlist, Review, ProductImage
from django.db import connection, reset_queries
from django.test import override_settings
from django.test.utils import CaptureQueriesContext

@override_settings(AXES_ENABLED=False)
class ProductListPerformanceTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Create 10 products
        for i in range(10):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=100,
                stock_quantity=10,
                category=self.category,
                vendor=self.vendor,
                description='Test description',
                is_active=True
            )
            # Add an image
            ProductImage.objects.create(product=product, image='test.jpg', alt_text='test')

            # Add a review
            Review.objects.create(
                product=product,
                user=self.user,
                rating=5,
                comment='Great!'
            )

            # Add to wishlist for even products
            if i % 2 == 0:
                Wishlist.objects.create(user=self.user, product=product)

    def test_product_list_queries(self):
        url = reverse('api_products')

        # Warmup
        self.client.get(url)

        reset_queries()

        with CaptureQueriesContext(connection) as queries:
             response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        count = len(queries)
        print(f"Number of queries: {count}")

        # Optimized query count should be low (expected around 4-6 queries)
        self.assertLess(count, 10, f"Expected optimized query count to be low, got {count}")
