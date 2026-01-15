import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from store.models import Vendor, Product, Order, OrderItem, Category
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
class TestVendorAnalytics:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testvendor', password='password')
        self.vendor = Vendor.objects.create(name='Test Vendor', created_by=self.user, slug='test-vendor')
        self.category = Category.objects.create(name='Test Category', slug='test-category')

        # Create products
        self.product1 = Product.objects.create(
            name='Product 1', slug='p1', price=100.00, stock_quantity=100,
            category=self.category, vendor=self.vendor
        )
        self.product2 = Product.objects.create(
            name='Product 2', slug='p2', price=200.00, stock_quantity=100,
            category=self.category, vendor=self.vendor
        )

        # Create orders
        now = timezone.now()

        # Order 1: Paid, Today
        o1 = Order.objects.create(
            first_name='A', last_name='B', email='a@b.com', paid=True, created_at=now
        )
        OrderItem.objects.create(order=o1, product=self.product1, vendor=self.vendor, price=100, quantity=2) # 200
        OrderItem.objects.create(order=o1, product=self.product2, vendor=self.vendor, price=200, quantity=1) # 200

        # Order 2: Paid, 10 days ago (Monthly, not Weekly)
        o2 = Order.objects.create(
            first_name='A', last_name='B', email='a@b.com', paid=True,
            created_at=now - timedelta(days=10)
        )
        # Hack to set created_at for auto_now_add=True
        Order.objects.filter(id=o2.id).update(created_at=now - timedelta(days=10))
        # Refetch to ensure relation works if needed, but OrderItem uses order.created_at via join
        # Actually OrderItem doesn't store date, it joins order.

        OrderItem.objects.create(order=o2, product=self.product1, vendor=self.vendor, price=100, quantity=1) # 100

        # Order 3: Paid, 40 days ago (Total only)
        o3 = Order.objects.create(
            first_name='A', last_name='B', email='a@b.com', paid=True,
            created_at=now - timedelta(days=40)
        )
        Order.objects.filter(id=o3.id).update(created_at=now - timedelta(days=40))
        OrderItem.objects.create(order=o3, product=self.product1, vendor=self.vendor, price=100, quantity=1) # 100

        # Order 4: Not Paid (Should be ignored)
        o4 = Order.objects.create(
            first_name='A', last_name='B', email='a@b.com', paid=False, created_at=now
        )
        OrderItem.objects.create(order=o4, product=self.product1, vendor=self.vendor, price=100, quantity=5)

    def test_analytics_calculation(self):
        self.client.force_authenticate(user=self.user)
        # Assuming the URL is correct, otherwise need to check urls.py
        # Based on api_views.py it seems to be mapped. Let's try finding it or using hardcoded path.
        # usually /api/vendor/analytics/

        url = '/api/v1/vendor/analytics/'
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        data = response.data

        # Expected Revenue:
        # Weekly: Order 1 = 2*100 + 1*200 = 400
        # Monthly: Order 1 + Order 2 = 400 + 100 = 500
        # Total: Order 1 + Order 2 + Order 3 = 400 + 100 + 100 = 600

        assert float(data['revenue']['weekly']) == 400.00
        assert float(data['revenue']['monthly']) == 500.00
        assert float(data['revenue']['total']) == 600.00

        # Verify Orders count
        # Should be 3 distinct paid orders
        assert data['orders']['total'] == 3
