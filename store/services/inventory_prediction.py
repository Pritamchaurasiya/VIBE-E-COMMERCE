from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from ..models import OrderItem, InventoryPrediction
import math

class InventoryPredictionService:
    @staticmethod
    def predict_demand(product, days=30):
        """
        Predict demand for the next 'days' using simple Moving Average.
        """
        # Look back 90 days
        lookback_days = 90
        start_date = timezone.now() - timedelta(days=lookback_days)

        # Get daily sales
        sales_data = OrderItem.objects.filter(
            product=product,
            order__created_at__gte=start_date
        ).extra(select={'date': 'date(created_at)'}).values('date').annotate(
            qty=Sum('quantity')
        )

        total_sales = sum(item['qty'] for item in sales_data)
        daily_avg = total_sales / lookback_days if lookback_days > 0 else 0

        # Generate predictions
        predictions = []
        current_date = timezone.now().date()

        for i in range(1, days + 1):
            future_date = current_date + timedelta(days=i)
            # Simple linear projection + minimal randomness or seasonality could be added here
            # For now, just use daily_avg
            predicted_qty = math.ceil(daily_avg)

            prediction = InventoryPrediction(
                product=product,
                predicted_date=future_date,
                predicted_demand=predicted_qty,
                confidence_score=0.85 # Static confidence for simple MA
            )
            predictions.append(prediction)

        return predictions

    @staticmethod
    def generate_and_save_predictions(product):
        # Clear old future predictions
        InventoryPrediction.objects.filter(
            product=product,
            predicted_date__gte=timezone.now().date()
        ).delete()

        predictions = InventoryPredictionService.predict_demand(product)
        InventoryPrediction.objects.bulk_create(predictions)
        return predictions
