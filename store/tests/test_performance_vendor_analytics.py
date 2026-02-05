from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Vendor, Category, Product, Order, OrderItem, Profile

class VendorAnalyticsPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='vendoruser', password='password')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', city='City')
        # Link user to vendor
        self.user.vendor = self.vendor
        self.user.save()

        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Cat', slug='cat')
        self.product = Product.objects.create(
            name='Prod', slug='prod', price=Decimal('10.00'),
            category=self.category, vendor=self.vendor
        )

    def create_order(self, days_ago, quantity=1, paid=True, other_vendor=False):
        order_time = timezone.now() - timezone.timedelta(days=days_ago)
        order = Order.objects.create(
            first_name='John', paid=paid,
            payment_method='card'
        )
        # Hack to set created_at (auto_now_add makes it read-only usually, but we can update it)
        Order.objects.filter(id=order.id).update(created_at=order_time)
        order.refresh_from_db()

        if other_vendor:
            other_vendor_obj = Vendor.objects.create(name='Other', slug='other', city='City')
            prod = Product.objects.create(name='Other', slug='other', price=Decimal('10.00'), category=self.category, vendor=other_vendor_obj)
            OrderItem.objects.create(order=order, product=prod, vendor=other_vendor_obj, price=prod.price, quantity=quantity)
        else:
            OrderItem.objects.create(order=order, product=self.product, vendor=self.vendor, price=self.product.price, quantity=quantity)
        return order

    def test_analytics_calculation_correctness(self):
        # 1. Today (included in all) - $10
        self.create_order(days_ago=0, quantity=1)

        # 2. 6 days ago (included in all) - $20
        self.create_order(days_ago=6, quantity=2)

        # 3. 8 days ago (included in monthly, total; excluded from weekly) - $30
        self.create_order(days_ago=8, quantity=3)

        # 4. 20 days ago (included in monthly, total; excluded from weekly) - $40
        self.create_order(days_ago=20, quantity=4)

        # 5. 31 days ago (included in total; excluded from monthly, weekly) - $50
        self.create_order(days_ago=31, quantity=5)

        # 6. Unpaid (excluded from all)
        self.create_order(days_ago=0, quantity=10, paid=False)

        # 7. Other vendor (excluded from all)
        self.create_order(days_ago=0, quantity=10, other_vendor=True)

        # Expected:
        # Total: 10 + 20 + 30 + 40 + 50 = 150
        # Monthly (< 30 days): 10 + 20 + 30 + 40 = 100
        # Weekly (< 7 days): 10 + 20 = 30

        url = reverse('api_vendor_analytics')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        revenue = response.data['revenue']

        self.assertEqual(float(revenue['total']), 150.0)
        self.assertEqual(float(revenue['monthly']), 100.0)
        self.assertEqual(float(revenue['weekly']), 30.0)
