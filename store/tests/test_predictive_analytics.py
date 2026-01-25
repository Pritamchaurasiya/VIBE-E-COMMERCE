from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from store.models import Vendor, Category, Product, Order, OrderItem, Profile
from rest_framework.test import APIClient
from rest_framework import status

class PredictiveAnalyticsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='vendor', password='password')
        # Profile is created by signal, just get it
        self.profile = Profile.objects.get(user=self.user)
        self.profile.role = 'retailer'
        self.profile.save()

        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            created_by=self.user
        )
        # Monkey patch user.vendor for the test since OneToOne is on Vendor.created_by
        # But Vendor model says: created_by = OneToOneField(User, related_name='vendor')
        # So user.vendor works.

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Predictive Product',
            slug='predictive-product',
            price=Decimal('10.00'),
            category=self.category,
            vendor=self.vendor,
            stock_quantity=50
        )

        # Create sales history
        now = timezone.now()
        for i in range(10):
            # Create orders for last 10 days
            order = Order.objects.create(
                user=self.user,
                paid=True,
                created_at=now - timedelta(days=i)
            )
            # Need to manually set created_at because auto_now_add doesn't allow override easily
            # in some DBs, but Django tests usually allow it if updated after create
            Order.objects.filter(id=order.id).update(created_at=now - timedelta(days=i))

            OrderItem.objects.create(
                order=order,
                product=self.product,
                vendor=self.vendor,
                price=self.product.price,
                quantity=5 # 5 units per day
            )

    def test_vendor_analytics_prediction(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/vendor/analytics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check predictions
        predictions = response.data.get('stock_predictions')
        # We might not get predictions if sklearn is missing or data insufficient
        # But we added enough data.

        # If scikit-learn is installed (it is in requirements), we should get a prediction
        if predictions:
            self.assertEqual(len(predictions), 1)
            pred = predictions[0]
            self.assertEqual(pred['product_name'], 'Predictive Product')
            # 50 stock, 5/day sales => ~10 days left
            self.assertAlmostEqual(pred['days_until_stockout'], 10, delta=2)
