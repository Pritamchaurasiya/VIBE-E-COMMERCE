from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserPreference, Product
from .serializers import ProductSerializer

class UserCustomizationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user customization settings."""
        prefs = UserPreference.objects.filter(user=request.user)
        return Response({
            'preferences': {p.preference_key: p.preference_value for p in prefs},
            # Add other settings like theme, notifications, etc.
        })

    def post(self, request):
        """Update user customization settings."""
        data = request.data
        for key, value in data.items():
            UserPreference.objects.update_or_create(
                user=request.user,
                preference_key=key,
                defaults={'preference_value': value, 'preference_type': 'customization'}
            )
        return Response({'success': True})

class PersonalizedFeedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get a personalized product feed based on user preferences."""
        # 1. Get preferred categories
        preferred_categories = UserPreference.objects.filter(
            user=request.user,
            preference_key='preferred_category'
        ).values_list('preference_value', flat=True)

        queryset = Product.objects.filter(is_active=True)

        if preferred_categories:
            queryset = queryset.filter(category__name__in=preferred_categories)

        # 2. Add logic for other preferences (price range, brand, etc.)

        serializer = ProductSerializer(queryset[:20], many=True)
        return Response(serializer.data)
