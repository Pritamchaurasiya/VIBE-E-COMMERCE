import random
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

class WeatherView(APIView):
    """
    API view for fetching weather data (Mocked for now).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        city = request.query_params.get('city', 'Varanasi')

        # Mock data generation
        current_temp = random.randint(25, 35)
        conditions = ['Sunny', 'Cloudy', 'Rainy', 'Partly Cloudy']
        current_condition = random.choice(conditions)

        forecast = []
        today = timezone.now().date()

        for i in range(1, 6):
            date = today + timedelta(days=i)
            forecast.append({
                'date': date.isoformat(),
                'temp_high': random.randint(30, 38),
                'temp_low': random.randint(20, 28),
                'condition': random.choice(conditions),
                'humidity': random.randint(40, 80)
            })

        return Response({
            'city': city,
            'current': {
                'temp': current_temp,
                'condition': current_condition,
                'humidity': random.randint(40, 70),
                'wind_speed': random.randint(5, 15)
            },
            'forecast': forecast
        })

class SoilHealthView(APIView):
    """
    API view for soil health information (Mocked).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        sample_id = request.query_params.get('sample_id')
        user = request.user

        # Return generic data if no specific sample
        return Response({
            'soil_health': {
                'nitrogen': 'Medium',
                'phosphorus': 'High',
                'potassium': 'Low',
                'ph_level': 6.5,
                'organic_carbon': '0.75%',
                'recommendations': [
                    'Apply NPK 10:26:26 fertilizer',
                    'Add organic manure',
                    'Use bio-fertilizers'
                ],
                'suitable_crops': ['Wheat', 'Mustard', 'Potato']
            }
        })

class MandiPricesView(APIView):
    """
    API view for mandi (market) prices (Mocked).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        market = request.query_params.get('market', 'Local Mandi')

        crops = [
            {'name': 'Wheat', 'price': 2100, 'trend': 'up'},
            {'name': 'Rice (Basmati)', 'price': 3500, 'trend': 'stable'},
            {'name': 'Mustard', 'price': 5400, 'trend': 'down'},
            {'name': 'Potato', 'price': 1200, 'trend': 'up'},
            {'name': 'Tomato', 'price': 2500, 'trend': 'up'},
            {'name': 'Onion', 'price': 1800, 'trend': 'stable'},
        ]

        # Add some randomness to prices
        for crop in crops:
            variation = random.randint(-100, 100)
            crop['price'] += variation

        return Response({
            'market': market,
            'last_updated': timezone.now().isoformat(),
            'prices': crops
        })
