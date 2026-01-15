import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from store.models import Category, Vendor, Product, ProductImage, Review, Wishlist
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestProductListPerformance:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

    def create_products(self, count):
        products = []
        for i in range(count):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=100.00,
                category=self.category,
                vendor=self.vendor,
                description='Test Description',
                stock_quantity=10
            )
            # Add image
            ProductImage.objects.create(product=product, image='test.jpg')
            # Add review
            Review.objects.create(
                product=product,
                user=self.user,
                rating=5,
                comment='Great!'
            )
            products.append(product)

        # Add first product to wishlist
        if products:
            Wishlist.objects.create(user=self.user, product=products[0])

        return products

    def test_product_list_queries(self, django_assert_num_queries):
        # Create 5 products
        self.create_products(5)

        url = reverse('api_products')

        # We expect a certain number of queries.
        # 1. Count products (pagination)
        # 2. Fetch products
        # 3. Fetch images (N queries)
        # 4. Fetch reviews (N queries for rating)
        # 5. Fetch reviews (N queries for count)
        # 6. Check wishlist (N queries)

        # With 5 products, if N+1 exists, we expect > 15 queries.
        # If optimized, should be constant (around 5-7 queries).

        # We expect 4 queries:
        # 1. Count (pagination)
        # 2. Products + Reviews (Join/Annotate)
        # 3. Images (Prefetch)
        # 4. Wishlist (Context)
        with django_assert_num_queries(4):
             response = self.client.get(url)
             assert response.status_code == status.HTTP_200_OK
             assert len(response.data['results']) == 5
