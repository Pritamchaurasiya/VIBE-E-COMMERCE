import logging
from django.db.models import Sum, Count
from django.utils import timezone
from .models import Order, UserInteraction, UserSession

logger = logging.getLogger(__name__)

class PredictiveService:
    """
    Service for predictive analytics logic.
    """

    @classmethod
    def predict_purchase_probability(cls, user):
        """
        Predict probability (0.0 to 1.0) that a user will make a purchase.
        Based on heuristics: recent activity, cart interactions, past orders.
        """
        if not user.is_authenticated:
            return 0.1

        # Feature 1: Recent Activity (active session in last hour)
        recent_sessions = UserSession.objects.filter(
            user=user,
            is_active=True,
            last_activity__gte=timezone.now() - timezone.timedelta(hours=1)
        ).exists()

        # Feature 2: Cart Activity (add to cart in last 24h)
        cart_adds = UserInteraction.objects.filter(
            user=user,
            interaction_type='add_to_cart',
            timestamp__gte=timezone.now() - timezone.timedelta(days=1)
        ).count()

        # Feature 3: Past Orders
        past_orders = Order.objects.filter(user=user, paid=True).count()

        score = 0.1 # Base probability

        if recent_sessions:
            score += 0.2

        if cart_adds > 0:
            score += 0.4
            if cart_adds > 3:
                score += 0.1

        if past_orders > 0:
            score += 0.1
            if past_orders > 5:
                score += 0.1

        return min(1.0, round(score, 2))
