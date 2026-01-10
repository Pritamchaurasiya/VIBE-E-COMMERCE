import logging
from decimal import Decimal
from django.utils import timezone
from django.db.models import Avg, Count
from store.models import Product, OrderItem, AnalyticsEvent

logger = logging.getLogger(__name__)

class DynamicPricingService:
    """
    Service for calculating dynamic prices based on demand, stock, and competitors.
    """

    @staticmethod
    def calculate_price(product: Product) -> dict:
        """
        Calculate dynamic price for a product.
        Returns a dict with 'price', 'discount_percentage', 'factors'.
        """
        base_price = product.mrp or product.price
        current_price = product.price

        # Factor 1: Stock Level (Scarcity)
        stock_factor = 1.0
        if product.stock_quantity <= 5:
            stock_factor = 1.10  # +10% if very low stock
        elif product.stock_quantity <= 20:
            stock_factor = 1.05  # +5% if low stock
        elif product.stock_quantity > 100:
            stock_factor = 0.95  # -5% if overstocked

        # Factor 2: Demand (Views/Cart Adds in last 24h)
        demand_factor = 1.0
        last_24h = timezone.now() - timezone.timedelta(hours=24)
        views = AnalyticsEvent.objects.filter(
            product=product,
            event_type='product_view',
            created_at__gte=last_24h
        ).count()

        if views > 100:
            demand_factor = 1.05
        elif views > 50:
            demand_factor = 1.02
        elif views < 5:
            demand_factor = 0.98

        # Factor 3: Expiry (if applicable - using created_at as proxy for age if no expiry)
        expiry_factor = 1.0
        # If product has batches with near expiry, we might want to discount.
        # This is a simplified check.

        # Calculate suggested price
        suggested_price = float(base_price) * stock_factor * demand_factor * expiry_factor

        # Safety bounds: Don't exceed MRP, don't go below cost (assuming cost is 60% of MRP)
        if product.mrp:
            suggested_price = min(suggested_price, float(product.mrp))
            min_price = float(product.mrp) * 0.6
            suggested_price = max(suggested_price, min_price)

        return {
            'original_price': float(current_price),
            'suggested_price': round(suggested_price, 2),
            'factors': {
                'stock_factor': stock_factor,
                'demand_factor': demand_factor,
                'views_24h': views
            }
        }
