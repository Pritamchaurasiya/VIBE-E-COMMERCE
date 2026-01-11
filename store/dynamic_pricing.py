from decimal import Decimal
from django.utils import timezone
from .models import Product, OrderItem

class DynamicPricingEngine:
    """
    Engine to calculate dynamic prices based on demand, stock, and time.
    """

    def calculate_price(self, product: Product) -> Decimal:
        base_price = product.price

        # 1. Stock-based adjustment
        # If stock is low (< 10), increase price by 5%
        if product.stock_quantity < 10:
            base_price *= Decimal('1.05')

        # 2. Demand-based adjustment (Sales in last 24h)
        last_24h = timezone.now() - timezone.timedelta(hours=24)
        recent_sales = OrderItem.objects.filter(
            product=product,
            order__created_at__gte=last_24h
        ).count()

        if recent_sales > 50:
            base_price *= Decimal('1.10') # High demand
        elif recent_sales > 20:
            base_price *= Decimal('1.05') # Moderate demand

        # 3. Time-based (e.g., Night pricing or Weekend surge - optional)

        return round(base_price, 2)

    def apply_dynamic_pricing(self):
        """Batch job to update product prices."""
        products = Product.objects.filter(is_active=True)
        for product in products:
            new_price = self.calculate_price(product)
            # You might want to store this in a separate 'dynamic_price' field
            # instead of overwriting the base price directly to avoid confusion.
            # For now, let's assume we update a cache or a specific field.
            pass
