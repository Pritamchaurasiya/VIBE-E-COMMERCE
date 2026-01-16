import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from store.models import Order, Product, Vendor, Category, User, OrderItem
from store.tracking_models import SystemAccessTracker
from django.utils import timezone

@pytest.mark.django_db
class TestBoltChanges:
    def test_dashboard_stats_view(self):
        client = APIClient()
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        client.force_authenticate(user=admin_user)

        # Create dummy data
        vendor = Vendor.objects.create(name="Vendor 1", slug="vendor-1")
        category = Category.objects.create(name="Cat 1", slug="cat-1")
        product = Product.objects.create(
            name="Prod 1", slug="prod-1", price=100,
            stock_quantity=10, vendor=vendor, category=category
        )

        # Create orders
        order1 = Order.objects.create(paid=True, status='delivered', paid_amount=100)
        OrderItem.objects.create(order=order1, product=product, vendor=vendor, price=100, quantity=1)

        order2 = Order.objects.create(paid=True, status='processing', paid_amount=100)
        OrderItem.objects.create(order=order2, product=product, vendor=vendor, price=100, quantity=1)

        order3 = Order.objects.create(paid=False, status='pending', paid_amount=0)

        url = reverse('api_dashboard_stats')
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()

        assert data['orders']['total'] == 3
        assert data['orders']['paid'] == 2
        assert data['orders']['pending'] == 1
        assert data['orders']['processing'] == 1
        assert data['orders']['delivered'] == 1

        # Verify revenue
        assert data['revenue']['total'] == 200.0

    def test_tracking_models_exist(self):
        user = User.objects.create_user('trackuser', 'track@example.com', 'password')
        tracker = SystemAccessTracker.objects.create(
            access_type='login',
            user=user,
            ip_address='127.0.0.1',
            risk_level='low',
            is_successful=True
        )
        assert tracker.id is not None
        assert SystemAccessTracker.objects.count() == 1
