"""
Weather API endpoints for the store app.
"""
import random
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

class WeatherView(APIView):
    """
    API view to get weather data for the user's location.
    Currently returns mock data for demonstration purposes.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # In a real app, we would get latitude/longitude from request or user profile
        # and call an external API like OpenWeatherMap.

        # Mock Data Generation
        conditions = ['Sunny', 'Cloudy', 'Rainy', 'Partly Cloudy']
        current_condition = random.choice(conditions)

        temp_base = 25
        if current_condition == 'Sunny':
            temp_base = 30
        elif current_condition == 'Rainy':
            temp_base = 22

        current_temp = temp_base + random.randint(-2, 3)

        forecast = []
        today = datetime.now()

        for i in range(5):
            day = today + timedelta(days=i)
            day_condition = random.choice(conditions)
            day_temp = temp_base + random.randint(-3, 3)
            forecast.append({
                'day': day.strftime('%a'),
                'temp': day_temp,
                'condition': day_condition
            })

        data = {
            'location': 'New Delhi, India',
            'current': {
                'temp': current_temp,
                'condition': current_condition,
                'humidity': random.randint(40, 80),
                'wind_speed': random.randint(5, 20),
                'precipitation': random.randint(0, 10) if current_condition == 'Rainy' else 0
            },
            'forecast': forecast
        }

        return Response(data, status=status.HTTP_200_OK)
