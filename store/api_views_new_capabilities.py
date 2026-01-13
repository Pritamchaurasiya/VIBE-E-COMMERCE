from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import ProductBatch, JourneyPoint, Product, Vendor, TrackingAlert
from .serializers import ProductBatchSerializer, JourneyPointSerializer
from .permissions import IsVendorUser

# ============================================
# SUPPLY CHAIN TRACEABILITY VIEWS
# ============================================

class SupplyChainBatchView(generics.ListCreateAPIView):
    """
    API for listing and creating product batches.
    """
    serializer_class = ProductBatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'vendor'):
            return ProductBatch.objects.filter(vendor=user.vendor)
        # Admins see all
        if user.is_staff:
            return ProductBatch.objects.all()
        return ProductBatch.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'vendor'):
            raise PermissionDenied("Only vendors can create batches.")
        serializer.save(vendor=user.vendor)

class SupplyChainDetailView(generics.RetrieveUpdateAPIView):
    """
    API for retrieving and updating batch details.
    Publicly accessible for traceability (read-only), but updates require auth.
    """
    serializer_class = ProductBatchSerializer
    lookup_field = 'batch_id'

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if self.request.method in permissions.SAFE_METHODS:
             return ProductBatch.objects.all()
        # For updates, restrict to vendor or staff
        if user.is_staff:
             return ProductBatch.objects.all()
        if hasattr(user, 'vendor'):
             return ProductBatch.objects.filter(vendor=user.vendor)
        return ProductBatch.objects.none()

class JourneyPointView(generics.CreateAPIView):
    """
    API to add a journey point (scan event).
    """
    serializer_class = JourneyPointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        batch_id = self.kwargs.get('batch_id')
        batch = get_object_or_404(ProductBatch, batch_id=batch_id)

        # Verify user permission (Vendor or Logistics partner)
        # For simplicity, allowing vendor or staff
        if not (self.request.user.is_staff or (hasattr(self.request.user, 'vendor') and self.request.user.vendor == batch.vendor)):
             raise PermissionDenied("You do not have permission to update this batch.")

        # Update batch current location and status
        point = serializer.save(batch=batch)
        batch.current_location = point.location
        if point.status:
             # Map point status to batch status if applicable
             # For now, just update location
             pass
        batch.save()

# ============================================
# SECURITY DASHBOARD VIEW
# ============================================

class SecurityDashboardView(APIView):
    """
    API for security dashboard data.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        from django.db.models import Count
        from django.utils import timezone

        # Recent Alerts
        alerts = TrackingAlert.objects.all().order_by('-created_at')[:20]

        # Stats
        total_alerts = TrackingAlert.objects.count()
        critical_alerts = TrackingAlert.objects.filter(severity='critical').count()
        unresolved_alerts = TrackingAlert.objects.exclude(status='resolved').count()

        # Alerts by Type
        alerts_by_type = TrackingAlert.objects.values('alert_type').annotate(count=Count('id'))

        return Response({
            'summary': {
                'total_alerts': total_alerts,
                'critical_alerts': critical_alerts,
                'unresolved_alerts': unresolved_alerts,
            },
            'alerts_by_type': alerts_by_type,
            'recent_alerts': [
                {
                    'id': a.id,
                    'title': a.title,
                    'severity': a.severity,
                    'status': a.status,
                    'created_at': a.created_at,
                    'description': a.description
                } for a in alerts
            ]
        })


# ============================================
# DYNAMIC PRICING VIEWS
# ============================================

from .models import DynamicPricingRule
from .serializers import DynamicPricingRuleSerializer
from .services.dynamic_pricing import DynamicPricingService

class DynamicPricingRuleView(generics.ListCreateAPIView):
    """
    API to manage dynamic pricing rules.
    """
    serializer_class = DynamicPricingRuleSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = DynamicPricingRule.objects.all()

class DynamicPriceView(APIView):
    """
    API to get dynamic price for a product.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        dynamic_price = DynamicPricingService.calculate_price(product)

        return Response({
            'product_id': product.id,
            'base_price': product.price,
            'dynamic_price': dynamic_price,
            'currency': 'INR'
        })

# ============================================
# INVENTORY PREDICTION VIEWS
# ============================================

from .models import InventoryPrediction
from .serializers import InventoryPredictionSerializer
from .services.inventory_prediction import InventoryPredictionService

class InventoryPredictionView(generics.ListAPIView):
    """
    API to get inventory predictions.
    """
    serializer_class = InventoryPredictionSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorUser]

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if not product_id:
            return InventoryPrediction.objects.none()

        product = get_object_or_404(Product, id=product_id)

        # Verify ownership
        if hasattr(self.request.user, 'vendor') and product.vendor != self.request.user.vendor:
             raise PermissionDenied("You do not own this product.")

        # Generate fresh if needed (or cron job does it)
        # For demo, generate on fly if empty
        if not InventoryPrediction.objects.filter(product=product).exists():
            InventoryPredictionService.generate_and_save_predictions(product)

        return InventoryPrediction.objects.filter(product=product)
