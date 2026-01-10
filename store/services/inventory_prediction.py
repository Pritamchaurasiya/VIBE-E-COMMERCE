import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Avg
from store.models import Product, OrderItem

logger = logging.getLogger(__name__)

class InventoryPredictionService:
    """
    Service for predicting inventory depletion and restocking needs.
    """

    @staticmethod
    def predict_restock_date(product: Product) -> dict:
        """
        Predict when a product will run out of stock.
        """
        # Analyze last 30 days of sales
        last_30_days = timezone.now() - timedelta(days=30)
        sales_data = OrderItem.objects.filter(
            product=product,
            order__created_at__gte=last_30_days
        ).aggregate(total_sold=Sum('quantity'))

        total_sold = sales_data['total_sold'] or 0
        avg_daily_sales = total_sold / 30.0

        if avg_daily_sales <= 0:
            return {
                'avg_daily_sales': 0,
                'days_until_out_of_stock': None,
                'predicted_out_of_stock_date': None,
                'status': 'stagnant'
            }

        current_stock = product.stock_quantity
        days_left = current_stock / avg_daily_sales

        predicted_date = timezone.now() + timedelta(days=days_left)

        return {
            'avg_daily_sales': round(avg_daily_sales, 2),
            'days_until_out_of_stock': round(days_left, 1),
            'predicted_out_of_stock_date': predicted_date.date().isoformat(),
            'status': 'critical' if days_left < 7 else 'healthy'
        }
