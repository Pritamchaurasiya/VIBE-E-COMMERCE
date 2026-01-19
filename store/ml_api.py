"""
ML API endpoints for Price Prediction and Crop Advice.
"""
from datetime import datetime, timedelta
import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.db.models import Avg, Count
from django.utils import timezone
from .models import Product, OrderItem, Crop, Order
from .ml_analytics import get_ml_engine

@api_view(['GET'])
@permission_classes([AllowAny])
def predict_price(request, product_id):
    """
    Predict price trend for a product using simple linear regression
    on historical order data.
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get historical data (simplified for now: average daily price)
    # in a real scenario we'd use a dedicated PriceHistory model
    # Here we use OrderItems as a proxy for historical "sold at" prices
    end_date = timezone.now()
    start_date = end_date - timedelta(days=90)

    order_items = OrderItem.objects.filter(
        product=product,
        order__created_at__range=(start_date, end_date),
        order__paid=True
    ).values('order__created_at__date').annotate(
        avg_price=Avg('price')
    ).order_by('order__created_at__date')

    engine = get_ml_engine()
    engine.clear_data(f"price_{product_id}")

    data_points = []
    for item in order_items:
        price = float(item['avg_price'])
        engine.add_data_point(f"price_{product_id}", price)
        data_points.append({
            'date': item['order__created_at__date'],
            'price': price
        })

    # If not enough data, use current price and add some noise for demo
    if len(data_points) < 5:
        current_price = float(product.price)
        for i in range(10):
            # Mock historical data
            mock_price = current_price * (1 + random.uniform(-0.05, 0.05))
            engine.add_data_point(f"price_{product_id}", mock_price)

    prediction = engine.predict_next_value(f"price_{product_id}", forecast_periods=7)
    trend_analysis = engine.get_trend(f"price_{product_id}")

    return Response({
        'product': product.name,
        'current_price': product.price,
        'prediction': prediction.__dict__ if prediction else None,
        'trend_analysis': trend_analysis,
        'forecast_msg': f"Price expected to go {prediction.trend if prediction else 'stable'} in next 7 days."
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def crop_advice(request):
    """
    Get crop advice based on current season (month).
    """
    current_month = datetime.now().month

    # Simple Season Logic for India
    if 6 <= current_month <= 10:
        season = 'kharif'
    elif 11 <= current_month <= 3:
        season = 'rabi'
    else:
        season = 'zaid'

    crops = Crop.objects.filter(season__in=[season, 'all']).order_by('?')[:5]

    advice = []
    for crop in crops:
        advice.append({
            'crop_name': crop.name,
            'season': crop.get_season_display(),
            'tip': f"Best time to plant {crop.name} is now. Ensure proper irrigation." # Placeholder tip
        })

    return Response({
        'season': season.capitalize(),
        'advice': advice
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def smart_crop_calendar(request):
    """
    Get smart crop calendar advice.
    """
    # Just a wrapper or enhanced version of crop_advice
    return crop_advice(request)
