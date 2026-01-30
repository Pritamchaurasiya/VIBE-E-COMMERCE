"""
API views for Agri-Intelligence features.
"""
import logging
from datetime import timedelta
import random
from django.utils import timezone
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    UserFarm, SoilHealthReport, MandiPrice, WeatherLog, CropAdvisory,
    Crop
)
from .serializers import (
    UserFarmSerializer, SoilHealthReportSerializer, MandiPriceSerializer,
    WeatherLogSerializer, CropAdvisorySerializer
)

logger = logging.getLogger(__name__)

class UserFarmViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user farms.
    """
    serializer_class = UserFarmSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserFarm.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SoilHealthReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for soil health reports and recommendations.
    """
    serializer_class = SoilHealthReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SoilHealthReport.objects.filter(farm__user=self.request.user)

    def perform_create(self, serializer):
        report = serializer.save()
        # Auto-generate recommendations
        report.generate_recommendations()


class MandiPriceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing Mandi (Market) prices.
    """
    queryset = MandiPrice.objects.all().order_by('-arrival_date')
    serializer_class = MandiPriceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['state', 'district', 'market', 'commodity']
    search_fields = ['market', 'commodity', 'variety']

    @action(detail=False, methods=['get'])
    def trends(self, request):
        """
        Get price trends for a specific commodity and market.
        """
        market = request.query_params.get('market')
        commodity = request.query_params.get('commodity')

        if not market or not commodity:
            return Response(
                {'error': 'Market and commodity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = MandiPrice.objects.filter(
            market__iexact=market,
            commodity__iexact=commodity
        ).order_by('arrival_date')[:30]

        return Response(MandiPriceSerializer(data, many=True).data)


class WeatherViewSet(viewsets.ViewSet):
    """
    ViewSet for Weather data (Mocked/Integrated).
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        Get weather forecast for user's farms.
        """
        farms = UserFarm.objects.filter(user=request.user)
        if not farms.exists():
            return Response({'message': 'No farms found'}, status=status.HTTP_404_NOT_FOUND)

        # Mock weather service logic
        weather_data = []
        for farm in farms:
            # Check if we have a recent log
            today = timezone.now().date()
            log = WeatherLog.objects.filter(farm=farm, date=today).first()

            if not log:
                # Create a mock log if not exists (Simulation)
                log = WeatherLog.objects.create(
                    farm=farm,
                    date=today,
                    temp_max=random.uniform(25, 35),
                    temp_min=random.uniform(15, 22),
                    rainfall=random.choice([0, 0, 0, 5, 12]),
                    humidity=random.uniform(40, 80),
                    wind_speed=random.uniform(5, 15),
                    condition=random.choice(['Sunny', 'Cloudy', 'Partly Cloudy', 'Light Rain']),
                    forecast_data={
                        'tomorrow': {'condition': 'Sunny', 'temp_max': 32},
                        'day_after': {'condition': 'Cloudy', 'temp_max': 30}
                    }
                )

            weather_data.append(WeatherLogSerializer(log).data)

        return Response(weather_data)


class CropAdvisoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Expert Advisory Q&A.
    """
    serializer_class = CropAdvisorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['topic', 'status', 'crop']
    search_fields = ['question', 'answer']

    def get_queryset(self):
        # Users see their own questions + public answered questions
        user = self.request.user
        return CropAdvisory.objects.filter(
            user=user
        ) | CropAdvisory.objects.filter(
            is_public=True,
            status='answered'
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
