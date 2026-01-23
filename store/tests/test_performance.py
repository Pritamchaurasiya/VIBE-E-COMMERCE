"""
Performance tests for the store app.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from store.models import Product, Category, Vendor, ProductImage, Wishlist, Review
from decimal import Decimal

class ProductPerformanceTest(TestCase):
    """Test performance of product list view."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.category = Category.objects.create(name='Test Category', slug='test-category')

        # Create 10 products
        for i in range(10):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('100.00'),
                category=self.category,
                vendor=self.vendor,
                is_active=True
            )
            # Add an image
            ProductImage.objects.create(product=product, image='test.jpg', alt_text='test')

            # Add to wishlist for even numbered products
            if i % 2 == 0:
                Wishlist.objects.create(user=self.user, product=product)

            # Add a review
            Review.objects.create(
                product=product,
                user=self.user,
                rating=5,
                title='Great',
                comment='Good product'
            )

    def test_product_list_queries(self):
        """
        Verify that ProductListView query count is optimized (constant queries).
        Reduced from ~52 to 4 queries for 10 products.
        """
        # First request to warm up (if any caching)
        # response = self.client.get(reverse('api_products'))

        # Capture queries
        # Expecting:
        # 1. Pagination count
        # 2. Products fetch (with annotations and joined tables)
        # 3. Images prefetch
        # 4. Wishlist IDs fetch
        with self.assertNumQueries(4):
             response = self.client.get(reverse('api_products'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
