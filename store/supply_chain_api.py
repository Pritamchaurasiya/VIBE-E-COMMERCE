from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import ProductBatch, JourneyPoint, Product
from .serializers import ProductSerializer

class SupplyChainView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, batch_id):
        batch = get_object_or_404(ProductBatch, batch_id=batch_id)
        journey = JourneyPoint.objects.filter(batch=batch).order_by('timestamp')

        journey_data = [{
            'stage': point.stage,
            'location': point.location,
            'timestamp': point.timestamp,
            'description': point.description,
            'handler': point.handler
        } for point in journey]

        return Response({
            'batch_id': batch.batch_id,
            'product': batch.product.name,
            'origin': batch.origin_location,
            'harvest_date': batch.harvest_date,
            'journey': journey_data
        })

class CreateBatchView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        # Implementation for creating batches
        return Response({'status': 'Not implemented yet'}, status=501)
