import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.utils import CaptureQueriesContext
from django.db import connection
from decimal import Decimal
from rest_framework.test import APIClient
from store.models import Vendor, Category, Product, ProductImage, Review, Wishlist

@pytest.mark.django_db
class TestProductListPerformance:
    def test_product_list_query_count(self):
        client = APIClient()

        # Setup data
        user = User.objects.create_user(username='testperf', password='password')
        reviewer2 = User.objects.create_user(username='reviewer2', password='password')
        vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')
        category = Category.objects.create(name='Test Category', slug='test-category')

        products = []
        for i in range(20):
            product = Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('100.00'),
                category=category,
                vendor=vendor,
                is_active=True
            )
            products.append(product)

            # Create images (dummy path)
            ProductImage.objects.create(product=product, image='products/test.jpg', alt_text='Test Image')
            ProductImage.objects.create(product=product, image='products/test2.jpg', alt_text='Test Image 2')

            # Create reviews
            Review.objects.create(product=product, user=user, rating=5, title='Great', comment='Good')
            Review.objects.create(product=product, user=reviewer2, rating=4, title='Good', comment='Nice')

        # Add some to wishlist
        for i in range(5):
            Wishlist.objects.create(user=user, product=products[i])

        client.force_authenticate(user=user)

        # Measure queries
        with CaptureQueriesContext(connection) as context:
            response = client.get(reverse('api_products'))

        assert response.status_code == 200

        # We expect a high number of queries currently (~81+).
        # We want to optimize this to be much lower, e.g. < 15.
        # This assertion should fail currently.
        print(f"Query count: {len(context)}")
        assert len(context) < 15, f"Too many queries: {len(context)}"
