from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from store.models import Vendor, Product, Category, Order, OrderItem, Profile
from store.api_views import VendorAnalyticsAPIView
from rest_framework.test import force_authenticate
from django.db import connection, reset_queries

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    REST_FRAMEWORK={
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ],
        'DEFAULT_THROTTLE_CLASSES': [], # Disable throttling
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
    }
)
class VendorAnalyticsPerformanceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vendor', password='password')
        # Profile is created by signal, so we fetch it instead of creating
        self.profile = Profile.objects.get(user=self.user)
        self.profile.role = 'vendor'
        self.profile.save()

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', created_by=self.user)
        self.category = Category.objects.create(name='Test Category', slug='test-category')

        # Create products
        self.products = []
        for i in range(10):
            self.products.append(Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                category=self.category,
                vendor=self.vendor,
                price=100,
                stock_quantity=100
            ))

        # Create orders
        self.order = Order.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            paid=True,
            status='delivered'
        )

        # Create many order items
        for i in range(50):
            OrderItem.objects.create(
                order=self.order,
                product=self.products[i % 10],
                vendor=self.vendor,
                price=100,
                quantity=1
            )

        self.factory = RequestFactory()
        self.view = VendorAnalyticsAPIView.as_view()

    def test_analytics_query_count(self):
        request = self.factory.get('/api/v1/vendor/analytics/')
        force_authenticate(request, user=self.user)

        # We expect a high number of queries initially
        # 1. User
        # 2. Vendor
        # 3. Products
        # 4. Products count (total)
        # 5. Products count (active)
        # 6. Products count (out of stock)
        # 7. Products count (low stock)
        # 8. Order items
        # 9. Reviews
        # 10. Avg rating
        # 11. Bulk orders
        # 12. Pending bulk count
        # 13. Top products

        reset_queries()

        # We expect around 7 queries after optimization (was 10)
        # 1. Product stats aggregation
        # 2. Revenue stats aggregation
        # 3. Reviews avg
        # 4. Reviews count
        # 5. Pending bulk count
        # 6. Top products
        # 7. Total orders count
        with self.assertNumQueries(7):
             response = self.view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['revenue']['total'], 5000.0)
        self.assertEqual(response.data['overview']['total_products'], 10)
