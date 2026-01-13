from decimal import Decimal
from django.utils import timezone
from ..models import DynamicPricingRule, OrderItem
from django.db.models import Sum

class DynamicPricingService:
    @staticmethod
    def calculate_price(product):
        """
        Calculate dynamic price for a product based on active rules.
        """
        rules = DynamicPricingRule.objects.filter(
            is_active=True
        ).order_by('-priority')

        base_price = product.price
        new_price = base_price

        # Filter relevant rules
        applicable_rules = []
        for rule in rules:
            if rule.product and rule.product != product:
                continue
            if rule.category and rule.category != product.category:
                continue
            applicable_rules.append(rule)

        for rule in applicable_rules:
            adjustment = Decimal('0.0')

            # Stock Based Rule
            if rule.rule_type == 'stock_based' and rule.threshold_stock is not None:
                if product.stock_quantity <= rule.threshold_stock:
                    adjustment = DynamicPricingService._calculate_adjustment(base_price, rule)

            # Demand Based Rule
            elif rule.rule_type == 'demand_based' and rule.threshold_sales_velocity is not None:
                # Calculate sales velocity (last 7 days)
                seven_days_ago = timezone.now() - timezone.timedelta(days=7)
                sales_count = OrderItem.objects.filter(
                    product=product,
                    order__created_at__gte=seven_days_ago
                ).aggregate(total=Sum('quantity'))['total'] or 0
                daily_velocity = sales_count / 7.0

                if daily_velocity >= rule.threshold_sales_velocity:
                    adjustment = DynamicPricingService._calculate_adjustment(base_price, rule)

            # Time Based Rule (Simple: weekend surge)
            elif rule.rule_type == 'time_based':
                weekday = timezone.now().weekday() # 0=Monday, 6=Sunday
                if weekday >= 5: # Weekend
                    adjustment = DynamicPricingService._calculate_adjustment(base_price, rule)

            new_price += adjustment

        # Enforce Min/Max
        # Note: We take the strictest min/max across all rules if multiple define it, or just the product's bounds if we had them.
        # Here we just check against the rule that applied the change, which is complex if multiple rules apply.
        # Simplified: Just ensure it doesn't drop below cost (if we knew it) or go too high.
        # For now, let's just return the calculated price.

        return max(Decimal('0.01'), new_price)

    @staticmethod
    def _calculate_adjustment(price, rule):
        if rule.adjustment_type == 'percentage':
            return price * (rule.adjustment_value / 100)
        else:
            return rule.adjustment_value
