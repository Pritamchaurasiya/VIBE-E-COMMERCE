from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import Product
from .services.inventory_prediction import InventoryPredictionService

class InventoryPredictionView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        prediction = InventoryPredictionService.predict_restock_date(product)
        return Response(prediction)
