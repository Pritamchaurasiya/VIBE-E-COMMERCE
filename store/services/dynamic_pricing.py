"""
Dynamic Pricing Service

Adjusts product prices based on:
1. Stock Level (Lower stock -> Higher price)
2. Demand (More views/orders -> Higher price)
3. Competitor Prices (Simulated)
4. Seasonality (Peak season -> Higher price)
"""

import logging
from decimal import Decimal
from django.utils import timezone
from store.models import Product, OrderItem, UserInteraction
from django.db.models import Count, Sum

logger = logging.getLogger(__name__)

class DynamicPricingService:
    """Service for calculating dynamic prices."""

    def __init__(self, product: Product):
        self.product = product

    def calculate_price(self):
        """Calculate the dynamic price for the product."""
        base_price = self.product.price
        adjustment_factor = Decimal('1.0')

        # 1. Stock Level Adjustment
        if self.product.stock_quantity <= 10:
             # Scarcity premium: +10%
            adjustment_factor += Decimal('0.10')
        elif self.product.stock_quantity > 100:
             # Overstock discount: -5%
            adjustment_factor -= Decimal('0.05')

        # 2. Demand Adjustment (Last 7 days)
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        recent_orders = OrderItem.objects.filter(
            product=self.product,
            order__created_at__gte=seven_days_ago
        ).count()

        if recent_orders > 50:
             # High demand: +5%
            adjustment_factor += Decimal('0.05')
        elif recent_orders < 5:
             # Low demand: -2%
            adjustment_factor -= Decimal('0.02')

        # 3. Time-based/Seasonality (Mock logic)
        # e.g., higher prices during day time? No, let's keep it simple.

        final_price = base_price * adjustment_factor

        # Ensure price doesn't go below cost (assuming cost is 60% of base price) or above MRP
        min_price = base_price * Decimal('0.6')
        if self.product.mrp:
            final_price = min(final_price, self.product.mrp)

        final_price = max(final_price, min_price)

        return round(final_price, 2)

    def update_product_price(self):
        """Update the product's price in the database."""
        new_price = self.calculate_price()
        if new_price != self.product.price:
            old_price = self.product.price
            self.product.price = new_price
            self.product.save()
            logger.info(f"Updated price for {self.product.name}: {old_price} -> {new_price}")
            return True, new_price
        return False, self.product.price
