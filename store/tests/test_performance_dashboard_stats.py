from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Order

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class DashboardStatsPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create some sample data
        now = timezone.now()

        # Today's paid order
        Order.objects.create(
            first_name='Today', last_name='Paid', email='test@example.com',
            paid=True, paid_amount=Decimal('100.00'), status='delivered',
            created_at=now
        )

        # Yesterday's paid order (Weekly, Monthly)
        Order.objects.create(
            first_name='Yesterday', last_name='Paid', email='test@example.com',
            paid=True, paid_amount=Decimal('200.00'), status='shipped',
        ).created_at = now - timedelta(days=1)
        # Hack to set created_at for auto_now_add=True field: update it after creation if needed,
        # but for tests, we can just let it be if we Mock timezone or use proper update.
        # Actually, auto_now_add sets it on creation. To override, we need to update it.
        Order.objects.filter(first_name='Yesterday').update(created_at=now - timedelta(days=1))

        # 10 days ago (Monthly)
        o = Order.objects.create(
            first_name='TenDays', last_name='Paid', email='test@example.com',
            paid=True, paid_amount=Decimal('300.00'), status='processing'
        )
        Order.objects.filter(id=o.id).update(created_at=now - timedelta(days=10))

        # 40 days ago (Old)
        o = Order.objects.create(
            first_name='Old', last_name='Paid', email='test@example.com',
            paid=True, paid_amount=Decimal('400.00'), status='confirmed'
        )
        Order.objects.filter(id=o.id).update(created_at=now - timedelta(days=40))

        # Pending order (Unpaid)
        Order.objects.create(
            first_name='Pending', last_name='Unpaid', email='test@example.com',
            paid=False, status='pending'
        )

        # Cancelled order
        Order.objects.create(
            first_name='Cancelled', last_name='Order', email='test@example.com',
            paid=False, status='cancelled'
        )

    def test_dashboard_stats_performance(self):
        url = reverse('api_dashboard_stats')

        # First run to warm up any caches (if any) and verify logic
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        # Verify correctness
        # Total revenue: 100 + 200 + 300 + 400 = 1000
        self.assertEqual(data['revenue']['total'], 1000.0)
        # Monthly revenue (<= 30 days): 100 + 200 + 300 = 600
        self.assertEqual(data['revenue']['monthly'], 600.0)
        # Weekly revenue (<= 7 days): 100 + 200 = 300
        self.assertEqual(data['revenue']['weekly'], 300.0)
        # Today revenue: 100
        self.assertEqual(data['revenue']['today'], 100.0)

        # Order counts
        # Total: 6
        self.assertEqual(data['orders']['total'], 6)
        # Paid: 4
        self.assertEqual(data['orders']['paid'], 4)
        # Pending: 1
        self.assertEqual(data['orders']['pending'], 1)
        # Cancelled: 1
        self.assertEqual(data['orders']['cancelled'], 1)

        # Now measure queries
        # Current implementation: 12 queries for orders/revenue + queries for products/users/vendors/etc.
        # Let's see how many we have.
        # Note: The view also fetches Product, User, Vendor stats.
        # Products: 4 queries
        # Users: 4 queries
        # Vendors: 2 queries
        # Recent orders: 1 query
        # Top products: 1 query
        # Total baseline around 12 (orders) + 12 (others) = 24 queries?

        # Verify optimization
        # We expect around 7 queries now (was significantly higher)
        # 1. User/Session/Auth (maybe cached/setup)
        # 2. Revenue aggregation
        # 3. Order count aggregation
        # 4. Product stats
        # 5. User stats
        # 6. Vendor stats
        # 7. Recent orders
        # 8. Top products
        # +1 margin

        # Note: If this fails with a different number, check the error message for the actual count
        # and what the extra queries are.
        # Running it with a range check logic manually if strict equality is flaky
        from django.db import connection
        with self.assertNumQueries(8):
             self.client.get(url)
