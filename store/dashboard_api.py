from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import UserAnalyticsDashboard
from .serializers import AnalyticsDashboardSerializer
from .permissions import IsVendorUser

class VendorDashboardConfigView(APIView):
    """
    API view to manage vendor dashboard configurations (widgets, layout).
    """
    permission_classes = [permissions.IsAuthenticated, IsVendorUser]

    def get(self, request):
        """Get all dashboard configurations for the user."""
        dashboards = UserAnalyticsDashboard.objects.filter(user=request.user)

        # If no dashboard exists, create a default one
        if not dashboards.exists():
            default_config = {
                'layout': [
                    {'id': 'revenue', 'x': 0, 'y': 0, 'w': 6, 'h': 4},
                    {'id': 'orders', 'x': 6, 'y': 0, 'w': 6, 'h': 4},
                    {'id': 'top_products', 'x': 0, 'y': 4, 'w': 6, 'h': 6},
                    {'id': 'recent_reviews', 'x': 6, 'y': 4, 'w': 6, 'h': 6},
                ],
                'theme': 'light'
            }
            UserAnalyticsDashboard.objects.create(
                user=request.user,
                dashboard_name='Default Vendor Dashboard',
                configuration=default_config,
                is_default=True
            )
            dashboards = UserAnalyticsDashboard.objects.filter(user=request.user)

        data = [{
            'id': d.id,
            'name': d.dashboard_name,
            'configuration': d.configuration,
            'is_default': d.is_default
        } for d in dashboards]

        return Response(data)

    def post(self, request):
        """Create a new dashboard configuration."""
        name = request.data.get('name')
        config = request.data.get('configuration', {})
        is_default = request.data.get('is_default', False)

        if not name:
            return Response(
                {'error': 'Dashboard name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if is_default:
            # Unset other defaults
            UserAnalyticsDashboard.objects.filter(
                user=request.user, is_default=True
            ).update(is_default=False)

        dashboard = UserAnalyticsDashboard.objects.create(
            user=request.user,
            dashboard_name=name,
            configuration=config,
            is_default=is_default
        )

        return Response({
            'id': dashboard.id,
            'name': dashboard.dashboard_name,
            'configuration': dashboard.configuration,
            'is_default': dashboard.is_default
        }, status=status.HTTP_201_CREATED)

class VendorDashboardDetailView(APIView):
    """
    API view to retrieve, update or delete a specific dashboard configuration.
    """
    permission_classes = [permissions.IsAuthenticated, IsVendorUser]

    def get(self, request, pk):
        """Get a specific dashboard."""
        dashboard = get_object_or_404(UserAnalyticsDashboard, id=pk, user=request.user)
        return Response({
            'id': dashboard.id,
            'name': dashboard.dashboard_name,
            'configuration': dashboard.configuration,
            'is_default': dashboard.is_default
        })

    def put(self, request, pk):
        """Update a dashboard configuration."""
        dashboard = get_object_or_404(UserAnalyticsDashboard, id=pk, user=request.user)

        name = request.data.get('name')
        config = request.data.get('configuration')
        is_default = request.data.get('is_default')

        if name:
            dashboard.dashboard_name = name
        if config:
            dashboard.configuration = config
        if is_default is not None:
            if is_default:
                # Unset other defaults
                UserAnalyticsDashboard.objects.filter(
                    user=request.user, is_default=True
                ).exclude(id=pk).update(is_default=False)
            dashboard.is_default = is_default

        dashboard.save()

        return Response({
            'id': dashboard.id,
            'name': dashboard.dashboard_name,
            'configuration': dashboard.configuration,
            'is_default': dashboard.is_default
        })

    def delete(self, request, pk):
        """Delete a dashboard configuration."""
        dashboard = get_object_or_404(UserAnalyticsDashboard, id=pk, user=request.user)
        dashboard.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
