from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from store.models import (
    Product, Vendor, ProductBatch, JourneyPoint, Category,
    SystemAccessTracker, TrackingConfiguration, BannedIP
)
from store.services.dynamic_pricing import DynamicPricingService
from store.services.inventory_prediction import InventoryPredictionService
from store.api_views import (
    SupplyChainView, DynamicPricingRecommendationsView,
    RestockPredictionsView
)
from rest_framework.test import APIClient
from decimal import Decimal

class NewCapabilitiesTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.user.vendor = self.vendor
        self.user.save()

        self.category = Category.objects.create(name='Test Category', slug='test-category')

        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('100.00'),
            mrp=Decimal('120.00'),
            stock_quantity=5, # Low stock
            category=self.category,
            vendor=self.vendor
        )

    def test_supply_chain_traceability(self):
        # Create batch and journey
        batch = ProductBatch.objects.create(
            batch_number='BATCH-001',
            product=self.product,
            vendor=self.vendor,
            quantity=100,
            manufacturing_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timezone.timedelta(days=365),
            current_location='Factory'
        )
        JourneyPoint.objects.create(
            batch=batch,
            location='Factory',
            description='Manufactured',
            status='manufactured'
        )

        response = self.client.get(f'/api/v1/supply-chain/{batch.batch_number}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['batch_number'], 'BATCH-001')
        self.assertEqual(len(response.data['journey']), 1)

    def test_dynamic_pricing_service(self):
        service = DynamicPricingService(self.product)
        # Low stock (5) should increase price
        # Base: 100. Stock <= 10: +10% => 110.
        # Demand: 0 orders (default) => -2% => 100 * (1 + 0.10 - 0.02) = 100 * 1.08 = 108.
        # Wait, the logic was:
        # adjustment = 1.0
        # Stock <= 10: += 0.10 -> 1.10
        # Orders < 5: -= 0.02 -> 1.08
        # Final = 100 * 1.08 = 108.

        price = service.calculate_price()
        self.assertEqual(price, Decimal('108.00'))

        # Test API
        response = self.client.get(f'/api/v1/dynamic-pricing/{self.product.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.data['recommended_price']), Decimal('108.00'))

    def test_inventory_prediction(self):
        # No sales yet, prediction should be None
        service = InventoryPredictionService(self.product)
        date = service.predict_stockout_date()
        self.assertIsNone(date)

        # Restock needed?
        # Sold 0. Target stock based on 0 sales is 0.
        # Current stock 5. Needed 0.
        needed = service.get_restock_recommendation()
        self.assertEqual(needed, 0)

        # Test API
        response = self.client.get('/api/v1/inventory/predictions/')
        self.assertEqual(response.status_code, 200)
        # Should be empty or contain product with 0 recommendation
        # My view logic appends if stockout_date or restock_amount > 0.
        # Here both are effectively null/0. So empty list.
        self.assertEqual(len(response.data['predictions']), 0)

    def test_security_models(self):
        # Test SystemAccessTracker creation (ensure model exists and works)
        tracker = SystemAccessTracker.objects.create(
            access_type='login_attempt',
            ip_address='127.0.0.1'
        )
        self.assertTrue(tracker.id)

        # Test BannedIP
        ban = BannedIP.objects.create(
            ip_address='192.168.1.1',
            reason='Malicious'
        )
        self.assertTrue(ban.id)

    def test_tracking_config(self):
        config = TrackingConfiguration.objects.create(
            category='user_actions',
            is_enabled=True
        )
        self.assertTrue(config.is_enabled)
