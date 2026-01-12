# Bolt Journal

## Performance Improvements
- Implemented `ProductBatch` and `JourneyPoint` with appropriate indexes for fast lookup by batch number.
- `SupplyChainService` uses atomic transactions to ensure data consistency when creating batches and journey points.
- `DynamicPricingService` optimized to filter rules by product and category efficiently.
- `InventoryPredictionService` uses aggregation `Sum` for efficient calculation of sales volume.

## Learnings
- Django `transaction.now()` is not a valid attribute; used `django.utils.timezone.now()` instead.
- Adding models to a large `models.py` file requires careful handling of imports and string references to avoid circular dependencies (e.g. `ForeignKey('Product', ...)`).
- Frontend tests require mocking of axios and backend APIs.
- When creating new API views that use `generics.CreateAPIView`, `perform_create` allows intercepting the save to use a Service layer.
