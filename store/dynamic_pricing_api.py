from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models import Product
from .services.dynamic_pricing import DynamicPricingService

class DynamicPricingView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        pricing_data = DynamicPricingService.calculate_price(product)
        return Response(pricing_data)
