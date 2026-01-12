from store.models import DynamicPricingRule, Product
from django.utils import timezone
from decimal import Decimal

class DynamicPricingService:
    @staticmethod
    def calculate_price(product):
        rules = DynamicPricingRule.objects.filter(
            product=product,
            is_active=True
        ).order_by('-priority')

        if not rules.exists():
             rules = DynamicPricingRule.objects.filter(
                category=product.category,
                is_active=True
            ).order_by('-priority')

        base_price = product.price

        for rule in rules:
            if rule.condition_type == 'low_stock':
                if product.stock_quantity <= rule.condition_value.get('threshold', 10):
                    base_price = base_price * rule.adjustment_factor
                    break # Apply highest priority rule only? Or chain? Let's apply first match for now.
            elif rule.condition_type == 'time_of_day':
                # Example implementation
                now = timezone.now()
                # Check if current hour is in range
                pass

        # Ensure within bounds
        if rules.exists():
            rule = rules.first()
            if rule.min_price and base_price < rule.min_price:
                base_price = rule.min_price
            if rule.max_price and base_price > rule.max_price:
                base_price = rule.max_price

        return base_price
