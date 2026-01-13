import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from store.models import (
    Product, Category, Vendor, ProductBatch, JourneyPoint,
    DynamicPricingRule, InventoryPrediction
)
from store.services.dynamic_pricing import DynamicPricingService
from store.services.inventory_prediction import InventoryPredictionService

@pytest.mark.django_db
class TestNewCapabilities:

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username='testuser', password='password')

    @pytest.fixture
    def vendor(self):
        user = User.objects.create_user(username='vendor', password='password')
        return Vendor.objects.create(name='Test Vendor', slug='test-vendor', created_by=user)

    @pytest.fixture
    def product(self, vendor):
        category = Category.objects.create(name='Test Cat', slug='test-cat')
        return Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('100.00'),
            category=category,
            vendor=vendor,
            stock_quantity=100
        )

    def test_supply_chain_batch_creation(self, api_client, vendor, product):
        api_client.force_authenticate(user=vendor.created_by)
        url = reverse('api_supply_chain_batch')
        data = {
            'batch_id': 'BATCH-001',
            'product': product.id,
            'quantity': 500,
            'production_date': '2023-01-01',
            'origin_location': 'Farm A',
            'current_location': 'Farm A'
        }
        response = api_client.post(url, data)
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response Error: {response.data}")
        assert response.status_code == status.HTTP_201_CREATED
        assert ProductBatch.objects.count() == 1
        assert ProductBatch.objects.get().batch_id == 'BATCH-001'

    def test_dynamic_pricing_logic(self, product):
        # Update product stock to trigger rule (stock <= threshold)
        product.stock_quantity = 40
        product.save()

        # Create a rule: 10% discount if stock <= 50
        rule = DynamicPricingRule.objects.create(
            name='Stock Discount',
            rule_type='stock_based',
            threshold_stock=50,
            adjustment_type='percentage',
            adjustment_value=Decimal('-10.00'),
            is_active=True
        )

        # Product stock is 40 (<= 50), so rule applies
        # Base price 100 -> 10% discount -> 90

        calculated_price = DynamicPricingService.calculate_price(product)
        assert calculated_price == Decimal('90.00')

    def test_inventory_prediction_service(self, product):
        # Service should return a list of predictions
        predictions = InventoryPredictionService.generate_and_save_predictions(product)
        assert len(predictions) == 30 # Default 30 days
        assert InventoryPrediction.objects.filter(product=product).count() == 30

    def test_security_dashboard_access(self, api_client, user):
        # Non-admin should fail
        api_client.force_authenticate(user=user)
        url = reverse('api_security_dashboard')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Admin should pass
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        api_client.force_authenticate(user=admin)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
