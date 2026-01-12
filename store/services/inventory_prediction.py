from store.models import Product, OrderItem
from django.db.models import Sum, F
from django.utils import timezone
from datetime import timedelta
import numpy as np

class InventoryPredictionService:
    @staticmethod
    def predict_stock_depletion(product_id):
        # Simple linear regression based on last 30 days sales
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)

        sales_data = OrderItem.objects.filter(
            product_id=product_id,
            order__created_at__range=(start_date, end_date)
        ).values('order__created_at__date').annotate(total_qty=Sum('quantity')).order_by('order__created_at__date')

        if not sales_data:
            return None

        dates = [d['order__created_at__date'] for d in sales_data]
        quantities = [d['total_qty'] for d in sales_data]

        avg_daily_sale = sum(quantities) / 30.0
        current_stock = Product.objects.get(id=product_id).stock_quantity

        if avg_daily_sale == 0:
            return 999 # Indefinite

        days_left = current_stock / avg_daily_sale
        return int(days_left)
