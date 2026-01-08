"""
Inventory Prediction Service

Predicts when a product will run out of stock based on sales velocity.
"""

import logging
from datetime import timedelta
from django.utils import timezone
from store.models import Product, OrderItem
from django.db.models import Sum

logger = logging.getLogger(__name__)

class InventoryPredictionService:
    """Service for predicting inventory depletion."""

    def __init__(self, product: Product):
        self.product = product

    def predict_stockout_date(self):
        """
        Predict the date when the product will go out of stock.
        Returns None if sales are zero.
        """
        # Analyze last 30 days of sales
        thirty_days_ago = timezone.now() - timedelta(days=30)

        total_sold = OrderItem.objects.filter(
            product=self.product,
            order__created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('quantity'))['total'] or 0

        if total_sold == 0:
            return None # Cannot predict

        daily_sales_velocity = total_sold / 30.0

        current_stock = self.product.stock_quantity
        if current_stock == 0:
            return timezone.now().date()

        days_until_stockout = current_stock / daily_sales_velocity

        predicted_date = timezone.now().date() + timedelta(days=int(days_until_stockout))
        return predicted_date

    def get_restock_recommendation(self):
        """
        Recommend restock quantity.
        Target: Maintain 30 days of inventory.
        """
        thirty_days_ago = timezone.now() - timedelta(days=30)
        total_sold_last_month = OrderItem.objects.filter(
            product=self.product,
            order__created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('quantity'))['total'] or 0

        target_stock = total_sold_last_month # Aim for 30 days cover
        needed = max(0, target_stock - self.product.stock_quantity)

        return needed
