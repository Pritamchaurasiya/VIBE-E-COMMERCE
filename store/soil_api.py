"""
API endpoints for Soil Health analysis and recommendations.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Product

class SoilHealthView(APIView):
    """
    API view to analyze soil health parameters and provide recommendations.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Analyze soil data and return recommendations.
        Expected JSON: { "n": 50, "p": 40, "k": 20, "ph": 6.5 }
        """
        try:
            n = float(request.data.get('n', 0))
            p = float(request.data.get('p', 0))
            k = float(request.data.get('k', 0))
            ph = float(request.data.get('ph', 7))
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid input values. Numbers required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        analysis = []
        recommendations = []
        recommended_products = []

        # Simple Rule Engine

        # Nitrogen
        if n < 50:
            analysis.append("Nitrogen (N) is Low.")
            recommendations.append("Apply Urea or Nitrogen-rich fertilizers.")
            # Find relevant products
            products = Product.objects.filter(
                description__icontains='urea'
            ).filter(is_active=True)[:2]
            if not products:
                 products = Product.objects.filter(
                    category__slug='fertilizers'
                ).filter(is_active=True)[:1]
            recommended_products.extend(products)
        elif n > 200:
            analysis.append("Nitrogen (N) is High.")
            recommendations.append("Avoid Nitrogen fertilizers for a while.")

        # Phosphorus
        if p < 20:
            analysis.append("Phosphorus (P) is Low.")
            recommendations.append("Apply DAP or Phosphorus-rich fertilizers.")
            products = Product.objects.filter(
                description__icontains='dap'
            ).filter(is_active=True)[:2]
            if not products:
                 products = Product.objects.filter(
                    category__slug='fertilizers'
                ).filter(is_active=True)[:1]
            recommended_products.extend(products)

        # Potassium
        if k < 100:
            analysis.append("Potassium (K) is Low.")
            recommendations.append("Apply MOP (Muriate of Potash).")
            products = Product.objects.filter(
                description__icontains='potash'
            ).filter(is_active=True)[:2]
            if not products:
                 products = Product.objects.filter(
                    category__slug='fertilizers'
                ).filter(is_active=True)[:1]
            recommended_products.extend(products)

        # pH
        if ph < 6.0:
            analysis.append(f"Soil is Acidic (pH {ph}).")
            recommendations.append("Use Lime to increase pH.")
        elif ph > 7.5:
            analysis.append(f"Soil is Alkaline (pH {ph}).")
            recommendations.append("Use Gypsum to reduce pH.")
        else:
            analysis.append(f"Soil pH ({ph}) is optimal.")

        # Format products
        products_data = []
        seen_ids = set()
        for prod in recommended_products:
            if prod.id not in seen_ids:
                products_data.append({
                    'id': prod.id,
                    'name': prod.name,
                    'slug': prod.slug,
                    'price': float(prod.price),
                    'image': prod.image.url if prod.image else None
                })
                seen_ids.add(prod.id)

        if not analysis:
            analysis.append("Soil parameters seem within normal ranges.")

        return Response({
            'analysis': analysis,
            'recommendations': recommendations,
            'products': products_data
        })
