import random
from datetime import timedelta
from django.utils import timezone

class DiseaseDiagnosisService:
    @staticmethod
    def diagnose(image):
        """
        Mock disease diagnosis from image.
        In a real app, this would call a TensorFlow/PyTorch model or external API.
        """
        diseases = [
            {'name': 'Leaf Rust', 'confidence': 0.95, 'treatment': 'Apply fungicide propiconazole.'},
            {'name': 'Powdery Mildew', 'confidence': 0.88, 'treatment': 'Spray sulfur or neem oil.'},
            {'name': 'Healthy', 'confidence': 0.99, 'treatment': 'Continue standard care.'},
            {'name': 'Early Blight', 'confidence': 0.75, 'treatment': 'Remove infected leaves and apply copper fungicide.'},
        ]
        # Simulate processing time
        return random.choice(diseases)

class PredictiveService:
    @staticmethod
    def predict_next_purchase(user):
        """
        Mock prediction for next purchase.
        """
        categories = ['Seeds', 'Fertilizers', 'Pesticides', 'Farm Tools']
        days_offset = random.randint(3, 30)
        predicted_date = timezone.now() + timedelta(days=days_offset)

        return {
            'predicted_category': random.choice(categories),
            'predicted_date': predicted_date.date().isoformat(),
            'confidence_score': round(random.uniform(0.6, 0.95), 2),
            'reason': 'Based on your seasonal purchase history and crop cycle.'
        }
