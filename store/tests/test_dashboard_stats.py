
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from store.models import Order, Product, OrderItem, Vendor, Category
from django.test.utils import CaptureQueriesContext
from django.db import connection
from decimal import Decimal

@pytest.mark.django_db
class TestDashboardStats:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='password'
        )
        self.client.force_authenticate(user=self.user)

        # Setup basic data
        self.vendor = Vendor.objects.create(name="Vendor 1", slug="vendor-1")
        self.category = Category.objects.create(name="Category 1", slug="category-1")
        self.product = Product.objects.create(
            name="Product 1",
            slug="product-1",
            price=Decimal("100.00"),
            category=self.category,
            vendor=self.vendor,
            stock_quantity=100
        )

        # Create orders
        # 1. Paid order today
        order1 = Order.objects.create(
            user=self.user,
            first_name="John",
            paid_amount=Decimal("200.00"),
            paid=True,
            status='delivered'
        )
        OrderItem.objects.create(order=order1, product=self.product, price=self.product.price, quantity=2, vendor=self.vendor)

        # 2. Paid order 10 days ago
        order2 = Order.objects.create(
            user=self.user,
            first_name="Jane",
            paid_amount=Decimal("100.00"),
            paid=True,
            status='shipped'
        )
        order2.created_at = timezone.now() - timezone.timedelta(days=10)
        order2.save()
        OrderItem.objects.create(order=order2, product=self.product, price=self.product.price, quantity=1, vendor=self.vendor)

        # 3. Pending order today
        order3 = Order.objects.create(
            user=self.user,
            first_name="Bob",
            paid_amount=Decimal("300.00"),
            paid=False,
            status='pending'
        )
        OrderItem.objects.create(order=order3, product=self.product, price=self.product.price, quantity=3, vendor=self.vendor)

    def test_dashboard_stats_performance(self):
        url = reverse('api_dashboard_stats')

        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)

        assert response.status_code == 200

        # Current implementation has around 12+ queries
        print(f"\nQuery count: {len(context.captured_queries)}")
        # for q in context.captured_queries:
        #     print(q['sql'])

        data = response.data
        assert data['orders']['total'] == 3
        assert data['orders']['paid'] == 2
        assert data['revenue']['total'] == 300.0 # 200 + 100
        assert data['revenue']['today'] == 200.0
