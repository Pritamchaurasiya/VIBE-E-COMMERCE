
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.test import override_settings
from store.models import Product, Category, Vendor, ProductImage, Review, Wishlist, Profile

@pytest.mark.django_db
@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    },
    AXES_CACHE='default',
    SESSION_ENGINE='django.contrib.sessions.backends.db',
    AXES_ENABLED=False,
    REST_FRAMEWORK={
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ],
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 20,
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
        'DEFAULT_THROTTLE_CLASSES': [], # Disable throttling
        'DEFAULT_FILTER_BACKENDS': [
            'rest_framework.filters.SearchFilter',
            'rest_framework.filters.OrderingFilter',
        ],
    }
)
def test_product_list_nplusone(django_assert_num_queries):
    # Setup data
    user = User.objects.create_user(username='testuser', password='password')
    Profile.objects.get_or_create(user=user)

    category = Category.objects.create(name='Test Category', slug='test-category')
    vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='Test City')

    products = []
    for i in range(10):
        product = Product.objects.create(
            name=f'Product {i}',
            slug=f'product-{i}',
            category=category,
            vendor=vendor,
            price=100.00,
            stock_quantity=10,
            description='Test description'
        )
        ProductImage.objects.create(product=product, image='test.jpg')
        Review.objects.create(product=product, user=user, rating=5, comment='Great')
        products.append(product)

    # Add to wishlist
    Wishlist.objects.create(user=user, product=products[0])

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse('api_products')

    # Warm up queries (auth etc) - optional but good practice
    # client.get(url)

    # Measure queries
    # Expected:
    # 1. Main product query
    # 2. Images query (prefetch)
    # 3. Session/Auth (if not cached/mocked perfectly)
    # Should be low single digits.
    # Without optimization it would be 1 (list) + 10 (images) + 10 (ratings) + 10 (reviews count) + 10 (wishlist) = ~41+

    with django_assert_num_queries(3):
        response = client.get(url)

    assert response.status_code == 200
    assert len(response.data['results']) == 10
