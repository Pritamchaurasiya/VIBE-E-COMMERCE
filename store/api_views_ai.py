from rest_framework import views, status, permissions
from rest_framework.response import Response
from .models import Disease
import random

class DiseaseDiagnosisView(views.APIView):
    """
    API view for AI-powered crop disease diagnosis.
    Accepts an image and returns a predicted disease with confidence.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if 'image' not in request.FILES:
            return Response({'error': 'Image file is required'}, status=status.HTTP_400_BAD_REQUEST)

        # In production, this would pass the image to a TensorFlow/PyTorch model
        # For now, we simulate a prediction using our Disease database
        diseases = Disease.objects.all()
        if not diseases.exists():
            # If no diseases in DB, return a generic response
            return Response({
                'disease': {
                    'name': 'Unknown Blight',
                    'symptoms': 'Yellowing leaves, spots.',
                    'prevention': 'Ensure proper drainage.',
                    'treatment': 'Consult an expert.',
                },
                'confidence': 75.0,
                'image_url': ''
            })

        predicted = random.choice(list(diseases))
        confidence = random.uniform(85.0, 99.9)

        return Response({
            'disease': {
                'name': predicted.name,
                'symptoms': predicted.symptoms,
                'prevention': predicted.prevention_tips,
                'treatment': 'Apply recommended fungicides immediately.',
            },
            'confidence': round(confidence, 2),
            # In a real app, we would process and return the annotated image URL
            'image_url': ''
        })
