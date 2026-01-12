from store.models import ProductBatch, JourneyPoint
from django.db import transaction
from django.utils import timezone

class SupplyChainService:
    @staticmethod
    def create_batch(product, vendor, quantity, location, expiration_date, batch_number, production_date=None):
        if not production_date:
            production_date = timezone.now().date()
        with transaction.atomic():
            batch = ProductBatch.objects.create(
                product=product,
                vendor=vendor,
                quantity=quantity,
                current_location=location,
                expiration_date=expiration_date,
                batch_number=batch_number,
                production_date=production_date
            )
            JourneyPoint.objects.create(
                batch=batch,
                location=location,
                status='created',
                notes='Batch created'
            )
            return batch

    @staticmethod
    def update_location(batch, location, status, notes='', user=None):
        batch.current_location = location
        batch.save()
        JourneyPoint.objects.create(
            batch=batch,
            location=location,
            status=status,
            notes=notes,
            recorded_by=user
        )
