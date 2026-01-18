
import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from store.models import Order, OrderItem, Product, Category, Vendor, Profile, UserCoin
from rest_framework import status
from django.test.utils import CaptureQueriesContext
from django.db import connection

@pytest.mark.django_db
class TestDashboardStatsPerformance:
    def setup_method(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.force_authenticate(user=self.admin_user)

        # Create necessary related objects for OrderItem
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            vendor=self.vendor,
            price=100
        )

    def create_orders(self, count):
        now = timezone.now()
        for i in range(count):
            order = Order.objects.create(
                user=self.admin_user,
                first_name='Test',
                last_name='User',
                email='test@example.com',
                paid=True,
                paid_amount=100,
                status='delivered',
                created_at=now
            )
            OrderItem.objects.create(
                order=order,
                product=self.product,
                vendor=self.vendor,
                price=100,
                quantity=1
            )

    def test_dashboard_stats_query_count(self):
        self.create_orders(5)

        url = reverse('api_dashboard_stats')

        # Warm up
        self.client.get(url)

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Queries should be minimized (around 8 queries)
        # 1. Revenue aggregation
        # 2. Order aggregation
        # 3. Product aggregation
        # 4. User aggregation
        # 5. Vendor count
        # 6. Vendor with products count
        # 7. Recent orders
        # 8. Top products
        assert len(ctx.captured_queries) <= 10, f"Too many queries: {len(ctx.captured_queries)}"
