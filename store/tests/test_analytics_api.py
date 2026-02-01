from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from store.models import Vendor, Product, Category, Order, OrderItem, Profile
from store.tests.test_config import TEST_USER_PASSWORD

class VendorAnalyticsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = TEST_USER_PASSWORD

        # Create user and vendor
        self.user = User.objects.create_user(username='vendor', password=self.password)
        # Profile might be created by signal
        Profile.objects.get_or_create(user=self.user, defaults={'role': 'retailer'})
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor', created_by=self.user)

        # Attach vendor to user explicitly if needed by the view logic (hasattr(user, 'vendor'))
        # The OneToOneField is related_name='vendor' on User model, so creating Vendor with created_by=user should be enough if the model is set up that way.
        # Let's check model definition again.
        # Vendor model: created_by = OneToOneField(User, related_name='vendor', ...)
        # So yes, user.vendor works.

        self.category = Category.objects.create(name='Test Category', slug='test-category')

        # Create product
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor
        )

        # Create orders
        self.now = timezone.now()

        # Order 1: Recent, Paid (Should count for all)
        self.order1 = Order.objects.create(
            first_name='John', last_name='Doe', email='john@example.com',
            paid=True, created_at=self.now
        )
        # Override created_at which is auto_now_add
        self.order1.created_at = self.now
        self.order1.save()

        OrderItem.objects.create(
            order=self.order1, product=self.product, vendor=self.vendor,
            price=Decimal('100.00'), quantity=2
        ) # Revenue: 200

        # Order 2: 10 days ago, Paid (Should count for monthly, total)
        self.order2 = Order.objects.create(
            first_name='Jane', last_name='Doe', email='jane@example.com',
            paid=True
        )
        self.order2.created_at = self.now - timezone.timedelta(days=10)
        self.order2.save()

        OrderItem.objects.create(
            order=self.order2, product=self.product, vendor=self.vendor,
            price=Decimal('100.00'), quantity=1
        ) # Revenue: 100

        # Order 3: 40 days ago, Paid (Should count for total only)
        self.order3 = Order.objects.create(
            first_name='Bob', last_name='Smith', email='bob@example.com',
            paid=True
        )
        self.order3.created_at = self.now - timezone.timedelta(days=40)
        self.order3.save()

        OrderItem.objects.create(
            order=self.order3, product=self.product, vendor=self.vendor,
            price=Decimal('100.00'), quantity=3
        ) # Revenue: 300

        # Order 4: Recent, Unpaid (Should not count)
        self.order4 = Order.objects.create(
            first_name='Alice', last_name='Wonder', email='alice@example.com',
            paid=False
        )
        self.order4.created_at = self.now
        self.order4.save()

        OrderItem.objects.create(
            order=self.order4, product=self.product, vendor=self.vendor,
            price=Decimal('100.00'), quantity=5
        )

    def test_vendor_analytics_revenue(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api_vendor_analytics'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        revenue = response.data['revenue']

        # Expected calculation:
        # Total: 200 + 100 + 300 = 600
        # Monthly (< 30 days): 200 + 100 = 300
        # Weekly (< 7 days): 200

        self.assertEqual(revenue['total'], 600.00)
        self.assertEqual(revenue['monthly'], 300.00)
        self.assertEqual(revenue['weekly'], 200.00)
