import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Product, Vendor, Category, User, ProductBatch
from datetime import date

@pytest.mark.django_db
def test_supply_chain_creation():
    client = APIClient()
    user = User.objects.create_user(username='vendor', password='password')
    client.force_authenticate(user=user)

    vendor = Vendor.objects.create(name="Test Vendor", slug="test-vendor", created_by=user)
    category = Category.objects.create(name="Seeds", slug="seeds")
    product = Product.objects.create(
        name="Hybrid Wheat", slug="hybrid-wheat",
        price=100, category=category, vendor=vendor
    )

    url = reverse('api_supply_chain_batch')
    data = {
        "batch_number": "BATCH001",
        "product": product.id,
        "vendor": vendor.id,
        "quantity": 500,
        "current_location": "Warehouse A",
        "expiration_date": "2025-01-01",
        "production_date": "2024-01-01" # Added missing field
    }

    response = client.post(url, data)
    if response.status_code != 201:
        print(response.data)
    assert response.status_code == status.HTTP_201_CREATED
    assert ProductBatch.objects.count() == 1
    assert ProductBatch.objects.first().journey.count() == 1

@pytest.mark.django_db
def test_dynamic_pricing():
    client = APIClient()
    vendor = Vendor.objects.create(name="Test Vendor", slug="test-vendor")
    category = Category.objects.create(name="Seeds", slug="seeds")
    product = Product.objects.create(
        name="Hybrid Wheat", slug="hybrid-wheat",
        price=100, category=category, vendor=vendor, stock_quantity=5
    )

    from store.models import DynamicPricingRule
    DynamicPricingRule.objects.create(
        product=product,
        condition_type='low_stock',
        condition_value={'threshold': 10},
        adjustment_factor=1.2
    )

    url = reverse('api_dynamic_pricing', args=[product.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['dynamic_price'] == 120.0 # 100 * 1.2
