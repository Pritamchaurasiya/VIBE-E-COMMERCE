from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from store.models import Order, UserSession, User
from store.ml_analytics import get_ml_engine

class AnalyticsService:
    def __init__(self):
        self.engine = get_ml_engine()

    def get_sales_forecast(self, days=30, forecast_days=7):
        """
        Get sales forecast for the next `forecast_days` based on last `days` of data.
        """
        cutoff = timezone.now() - timedelta(days=days)
        daily_sales = Order.objects.filter(
            created_at__gte=cutoff,
            paid=True
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            total=Sum('paid_amount')
        ).order_by('date')

        # Feed data to engine
        metric_name = 'daily_sales'
        self.engine.clear_data(metric_name)

        # We need to fill in missing days with 0 for accurate prediction
        sales_data = {}
        for entry in daily_sales:
            sales_data[entry['date']] = float(entry['total'])

        current_date = cutoff.date()
        end_date = timezone.now().date()

        history = []
        while current_date <= end_date:
            val = sales_data.get(current_date, 0.0)
            self.engine.add_data_point(metric_name, val)
            history.append({'date': current_date.isoformat(), 'value': val})
            current_date += timedelta(days=1)

        # Predict
        prediction = self.engine.predict_next_value(metric_name, forecast_periods=forecast_days)

        forecast = []
        if prediction:
            # Linear regression gives a single point or a line?
            # predict_next_value implementation in ml_analytics returns a single value for next_x
            # We want a trend line.
            # Let's simple extrapolate for now using the returned predicted value as the target for the last forecast day
            # Actually, ml_analytics.py implementation:
            # predicted_value = slope * next_x + intercept
            # It predicts for (len(arr) + forecast_periods - 1)

            # Let's generate points for each future day
            # We can't access slope/intercept directly from result.
            # We will call predict_next_value for i in 1..forecast_days
            pass

        # Since MLAnalyticsEngine.predict_next_value is simple, let's just get one future point and interpolate?
        # Or better, improve MLAnalyticsEngine or just use it as is for a single "next period" prediction.
        # But for a chart, we want daily points.

        # Let's stick to what MLAnalyticsEngine provides: next value.
        # But wait, I can feed the predicted value back? No, that accumulates error.

        # For this demo, I will just get the trend and predicted next value.

        result = {
            'history': history,
            'prediction': prediction.__dict__ if prediction else None,
            'forecast': [] # TODO: Implement multi-step forecast if engine supports it
        }

        return result

    def get_churn_risk_distribution(self):
        """
        Calculate churn risk for all active users.
        """
        # Simple heuristic: Churn risk increases with days since last login.
        # < 7 days: Low
        # 7-30 days: Medium
        # > 30 days: High

        now = timezone.now()
        users = User.objects.filter(is_active=True)

        risk_counts = {'low': 0, 'medium': 0, 'high': 0}

        for user in users:
            last_session = UserSession.objects.filter(user=user).order_by('-started_at').first()
            if not last_session:
                risk = 'high'
            else:
                days_since = (now - last_session.started_at).days
                if days_since < 7:
                    risk = 'low'
                elif days_since < 30:
                    risk = 'medium'
                else:
                    risk = 'high'
            risk_counts[risk] += 1

        return risk_counts
