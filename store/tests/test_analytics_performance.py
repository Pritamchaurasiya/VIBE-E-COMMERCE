from datetime import timedelta
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
        # Create user and vendor
        self.user = User.objects.create_user(username='vendor', password='password')
        # Create profile to satisfy signals/logic
        Profile.objects.get_or_create(user=self.user, role='retailer')

        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            slug='test-vendor',
            created_by=self.user,
            city='Test City'
        )

        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(name='Cat', slug='cat')
        self.product = Product.objects.create(
            name='Prod', slug='prod', price=Decimal('100.00'),
            category=self.category, vendor=self.vendor, stock_quantity=1000
        )

        # Populate data
        now = timezone.now()

        # 5 orders today (revenue: 5 * 100 * 1 = 500)
        self.create_orders(5, now)

        # 5 orders 10 days ago (revenue: 5 * 100 * 1 = 500) - Monthly but not weekly
        self.create_orders(5, now - timedelta(days=10))

        # 5 orders 40 days ago (revenue: 5 * 100 * 1 = 500) - Total but not monthly/weekly
        self.create_orders(5, now - timedelta(days=40))

    def create_orders(self, count, date):
        for i in range(count):
            order = Order.objects.create(
                user=self.user,
                first_name='Test',
                paid=True,
                paid_amount=Decimal('100.00')
            )
            # Manually set created_at
            order.created_at = date
            order.save()

            OrderItem.objects.create(
                order=order,
                product=self.product,
                vendor=self.vendor,
                price=Decimal('100.00'),
                quantity=1
            )

    def test_analytics_correctness(self):
        response = self.client.get(reverse('api_vendor_analytics'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        revenue = response.data['revenue']

        # Total: 15 orders * 100 = 1500
        self.assertEqual(float(revenue['total']), 1500.0)

        # Monthly: 10 orders (today + 10 days ago) * 100 = 1000
        self.assertEqual(float(revenue['monthly']), 1000.0)

        # Weekly: 5 orders (today) * 100 = 500
        self.assertEqual(float(revenue['weekly']), 500.0)
