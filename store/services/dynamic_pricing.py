import logging
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, F
from store.models import Product, AnalyticsEvent, OrderItem, Deal

logger = logging.getLogger(__name__)

class DynamicPricingService:
    """
    Service for calculating optimal prices based on demand and inventory.
    """

    @staticmethod
    def analyze_product_performance(product: Product, days: int = 7) -> dict:
        """
        Analyze views vs sales (conversion rate) for a product.
        """
        cutoff_date = timezone.now() - timedelta(days=days)

        # Get views
        views = AnalyticsEvent.objects.filter(
            product=product,
            event_type__in=['product_view', 'page_view'],
            created_at__gte=cutoff_date
        ).count()

        # Get sales
        sales = OrderItem.objects.filter(
            product=product,
            order__created_at__gte=cutoff_date,
            order__paid=True
        ).count()

        conversion_rate = (sales / views * 100) if views > 0 else 0.0

        return {
            'views': views,
            'sales': sales,
            'conversion_rate': conversion_rate
        }

    @staticmethod
    def get_pricing_recommendation(product: Product) -> dict:
        """
        Generate a pricing recommendation.
        """
        performance = DynamicPricingService.analyze_product_performance(product)
        views = performance['views']
        conversion = performance['conversion_rate']
        stock_status = 'high' if product.stock_quantity > 50 else 'low'

        recommendation = {
            'product_id': product.id,
            'product_name': product.name,
            'current_price': float(product.price),
            'action': 'hold',
            'suggested_price': float(product.price),
            'reason': 'Stable performance'
        }

        # Logic: High views, low conversion -> Price might be too high
        if views > 50 and conversion < 1.0:
            suggested_price = float(product.price) * 0.95  # 5% discount
            recommendation.update({
                'action': 'decrease',
                'suggested_price': round(suggested_price, 2),
                'reason': f"High interest ({views} views) but low conversion ({conversion:.1f}%). Consider 5% discount."
            })

        # Logic: Low stock, high conversion -> Can increase price or hold
        elif stock_status == 'low' and conversion > 5.0:
            suggested_price = float(product.price) * 1.05  # 5% increase
            recommendation.update({
                'action': 'increase',
                'suggested_price': round(suggested_price, 2),
                'reason': f"High demand ({conversion:.1f}% conversion) and low stock. Opportunity to increase margin."
            })

        # Logic: Low views -> Need exposure (Deal)
        elif views < 10 and product.created_at < timezone.now() - timedelta(days=30):
             recommendation.update({
                'action': 'promote',
                'reason': "Low visibility. Consider adding to Flash Sale or Deal of the Day."
            })

        return recommendation
