
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Product, Category, Vendor, ProductImage, Review, Wishlist
from django.contrib.auth.models import User
from decimal import Decimal

@pytest.fixture(autouse=True)
def override_settings(settings):
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
    settings.SESSION_ENGINE = 'django.contrib.sessions.backends.db'
    # Disable throttling to avoid Redis dependency
    if hasattr(settings, 'REST_FRAMEWORK'):
        rf = settings.REST_FRAMEWORK.copy()
        rf['DEFAULT_THROTTLE_CLASSES'] = []
        settings.REST_FRAMEWORK = rf

@pytest.mark.django_db
class TestProductListPerformance:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')

        # Create 10 products
        for i in range(10):
            p = Product.objects.create(
                name=f"Product {i}",
                slug=f"product-{i}",
                category=self.category,
                vendor=self.vendor,
                price=Decimal('100.00'),
                stock_quantity=10,
                is_active=True
            )
            # Add images
            ProductImage.objects.create(product=p, image=f"test_{i}.jpg")

            # Add review
            Review.objects.create(
                product=p,
                user=self.user,
                rating=5,
                comment="Great!",
                title="Review"
            )

            # Add to wishlist (for half)
            if i % 2 == 0:
                Wishlist.objects.create(user=self.user, product=p)

    def test_product_list_query_count(self, django_assert_max_num_queries):
        """
        Ensure Product List API executes a constant number of queries regardless of product count.
        Expected queries:
        1. Main product query (with annotations and joins)
        2. Prefetch images
        3. User/Session auth (handled by setup but request might trigger checks)
        4. Count query for pagination

        We expect around 4-5 queries. Without optimization it would be 10*3 + 1 = 31+.
        """
        url = reverse('api_products')

        # Warm up
        self.client.get(url)

        # The actual test
        # We allow a bit more than strict 4 to account for auth overheads if any
        with django_assert_max_num_queries(10):
            response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 10

        # Verify annotated fields are present and correct
        results = {p['slug']: p for p in response.data['results']}

        # Product 0
        p0 = results['product-0']
        assert p0['is_in_wishlist'] is True
        assert p0['average_rating'] == 5.0
        assert p0['review_count'] == 1
        assert len(p0['images']) == 1

        # Product 1
        p1 = results['product-1']
        assert p1['is_in_wishlist'] is False
