from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal
from store.models import (
    Product, Vendor, Category, Order, OrderItem, AnalyticsEvent,
    ProductBatch, JourneyPoint, RestockRecommendation, BannedIP,
    TrackingConfiguration
)
from store.services.inventory_prediction import InventoryPredictionService
from store.services.dynamic_pricing import DynamicPricingService

class NewCapabilitiesTest(TestCase):
    def setUp(self):
        # Create common data
        self.user = User.objects.create_user(username='testuser', password='password')
        self.vendor_user = User.objects.create_user(username='vendor', password='password')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', created_by=self.vendor_user)
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('100.00'),
            stock_quantity=10,
            low_stock_threshold=20,
            vendor=self.vendor,
            category=self.category,
            is_active=True
        )

    def test_inventory_prediction(self):
        # Create order history to simulate sales
        order = Order.objects.create(
            user=self.user,
            first_name='Test',
            last_name='User',
            email='test@example.com',
            paid=True,
            status='confirmed'
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            vendor=self.vendor,
            price=self.product.price,
            quantity=5
        )

        # Run prediction
        prediction = InventoryPredictionService.predict_stockout_date(self.product)
        self.assertIn('days_remaining', prediction)
        self.assertIn('velocity', prediction)

        # Check recommendation generation
        recs = InventoryPredictionService.generate_restock_recommendations_for_vendor(self.vendor)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0].product, self.product)

    def test_dynamic_pricing(self):
        # Simulate views (high interest)
        for _ in range(60):
            AnalyticsEvent.objects.create(
                event_type='product_view',
                product=self.product,
                session_id='test_session'
            )

        # Run pricing analysis
        rec = DynamicPricingService.get_pricing_recommendation(self.product)

        # Expectation: High views, 0 sales (from setup above we have 0 sales in this specific test scope unless we reuse)
        # Wait, I added sales in setUp? No, in test_inventory_prediction.
        # So here sales=0. 60 views, 0 sales = 0% conversion.
        # Should suggest price decrease.

        self.assertEqual(rec['action'], 'decrease')
        self.assertLess(rec['suggested_price'], float(self.product.price))

    def test_supply_chain_models(self):
        batch = ProductBatch.objects.create(
            batch_id='BATCH-001',
            product=self.product,
            vendor=self.vendor,
            quantity=100
        )
        JourneyPoint.objects.create(
            batch=batch,
            location='Farm',
            status='harvested',
            handler='Farmer John'
        )

        self.assertEqual(batch.journey.count(), 1)
        self.assertEqual(batch.journey.first().status, 'harvested')

    def test_banned_ip_logic(self):
        ip = '192.168.1.100'
        BannedIP.objects.create(ip_address=ip, reason='Test ban')

        # Test middleware logic helper (simulated)
        # We can't easily test middleware directly here without a request factory,
        # but we can test the model property
        banned_entry = BannedIP.objects.get(ip_address=ip)
        self.assertTrue(banned_entry.is_active)
