from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from store.models import Product, Category, Vendor, ProductImage, Review, Wishlist

class ProductPerformanceTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        # Create 10 products
        for i in range(10):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                category=self.category,
                vendor=self.vendor,
                price=100.00,
                stock_quantity=10
            )

            # Create 3 images per product
            for j in range(3):
                ProductImage.objects.create(
                    product=product,
                    image=f'products/image_{i}_{j}.jpg'
                )

            # Create 2 reviews per product (one from each user)
            Review.objects.create(
                product=product,
                user=self.user,
                rating=5,
                comment='Great product'
            )
            Review.objects.create(
                product=product,
                user=self.user2,
                rating=4,
                comment='Good product'
            )

        # Add 5 products to wishlist
        for i in range(5):
            product = Product.objects.get(slug=f'product-{i}')
            Wishlist.objects.create(user=self.user, product=product)

        self.client.force_authenticate(user=self.user)

    def test_product_list_query_count(self):
        # Initial run to warm up any startup queries (content types, permissions, etc)
        self.client.get('/api/v1/products/')

        # Execute with query capture
        # Expecting ~4 queries:
        # 1. Pagination count
        # 2. Main product query (with annotations)
        # 3. Images prefetch
        # 4. Wishlist IDs fetch
        with self.assertNumQueries(4):
             response = self.client.get('/api/v1/products/')

        self.assertEqual(response.status_code, 200)
