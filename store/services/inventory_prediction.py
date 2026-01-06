import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, F
from django.db.models.functions import Coalesce
from store.models import Product, OrderItem, RestockRecommendation, Vendor

logger = logging.getLogger(__name__)

class InventoryPredictionService:
    """
    Service for predicting inventory needs and suggesting restocks.
    """

    @staticmethod
    def calculate_sales_velocity(product: Product, days: int = 30) -> float:
        """
        Calculate daily sales velocity for a product over the last N days.
        """
        cutoff_date = timezone.now() - timedelta(days=days)

        # Sum quantity of items sold in confirmed/paid orders
        sales_data = OrderItem.objects.filter(
            product=product,
            order__created_at__gte=cutoff_date,
            order__paid=True
        ).aggregate(total_sold=Coalesce(Sum('quantity'), 0))

        total_sold = sales_data['total_sold']

        if total_sold == 0:
            return 0.0

        return float(total_sold) / days

    @staticmethod
    def predict_stockout_date(product: Product) -> dict:
        """
        Predict when a product will run out of stock.
        """
        velocity = InventoryPredictionService.calculate_sales_velocity(product)
        current_stock = product.stock_quantity

        if velocity <= 0:
            return {
                'days_remaining': 365,  # Arbitrary high number for slow movers
                'predicted_date': timezone.now().date() + timedelta(days=365),
                'velocity': 0.0
            }

        days_remaining = int(current_stock / velocity)
        predicted_date = timezone.now().date() + timedelta(days=days_remaining)

        return {
            'days_remaining': days_remaining,
            'predicted_date': predicted_date,
            'velocity': velocity
        }

    @staticmethod
    def generate_restock_recommendations_for_vendor(vendor: Vendor):
        """
        Generate restock recommendations for all products of a vendor.
        """
        products = Product.objects.filter(vendor=vendor, is_active=True)
        recommendations = []

        for product in products:
            prediction = InventoryPredictionService.predict_stockout_date(product)
            days_remaining = prediction['days_remaining']

            # If stock will run out in less than 14 days (or custom threshold)
            # Or if current stock is below low_stock_threshold
            should_restock = (
                days_remaining <= 14 or
                product.stock_quantity <= product.low_stock_threshold
            )

            if should_restock:
                # Suggest restock amount (e.g., for 30 days of sales)
                recommended_qty = int(prediction['velocity'] * 30)
                # Ensure at least minimum viable restock
                recommended_qty = max(recommended_qty, 10)

                recommendation = RestockRecommendation.objects.create(
                    product=product,
                    vendor=vendor,
                    predicted_stockout_date=prediction['predicted_date'],
                    recommended_quantity=recommended_qty,
                    confidence_score=0.85 if prediction['velocity'] > 0.5 else 0.50
                )
                recommendations.append(recommendation)

        return recommendations
