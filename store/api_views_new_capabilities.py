from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.shortcuts import get_object_or_404
from .models import ProductBatch, Product
from .serializers import ProductBatchSerializer
from .services.supply_chain import SupplyChainService
from .services.dynamic_pricing import DynamicPricingService
from .services.inventory_prediction import InventoryPredictionService

class SupplyChainBatchView(generics.ListCreateAPIView):
    queryset = ProductBatch.objects.all()
    serializer_class = ProductBatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Use service to create batch with initial journey point
        # This overrides standard save to ensure journey start
        SupplyChainService.create_batch(
            product=serializer.validated_data['product'],
            vendor=serializer.validated_data['vendor'],
            quantity=serializer.validated_data['quantity'],
            location=serializer.validated_data['current_location'],
            expiration_date=serializer.validated_data['expiration_date'],
            batch_number=serializer.validated_data['batch_number'],
            production_date=serializer.validated_data.get('production_date')
        )

class SupplyChainDetailView(generics.RetrieveUpdateAPIView):
    queryset = ProductBatch.objects.all()
    serializer_class = ProductBatchSerializer
    lookup_field = 'batch_number'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def patch(self, request, *args, **kwargs):
        # Custom patch to handle location updates via service
        instance = self.get_object()
        if 'current_location' in request.data:
            SupplyChainService.update_location(
                batch=instance,
                location=request.data['current_location'],
                status=request.data.get('status', 'in_transit'),
                notes=request.data.get('notes', ''),
                user=request.user
            )
            return Response(self.get_serializer(instance).data)
        return super().patch(request, *args, **kwargs)

class DynamicPricingView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        price = DynamicPricingService.calculate_price(product)
        return Response({
            'product_id': product.id,
            'original_price': product.price,
            'dynamic_price': price,
            'currency': 'INR'
        })

class InventoryPredictionView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, product_id):
        days = InventoryPredictionService.predict_stock_depletion(product_id)
        return Response({
            'product_id': product_id,
            'days_until_stockout': days,
            'prediction_date': '2023-10-27' # dynamic in real app
        })
