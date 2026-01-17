from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Coupon, Vendor, Category
from django.utils import timezone
import datetime
import json

class CouponSecurityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')

        # Create a vendor and category for products
        self.vendor = Vendor.objects.create(name="Test Vendor", slug="test-vendor", created_by=self.user)
        self.category = Category.objects.create(name="Test Category", slug="test-category")

        # Create a coupon
        self.coupon = Coupon.objects.create(
            code="TEST10",
            discount_type="percent",
            discount_value=10,
            valid_from=timezone.now() - datetime.timedelta(days=1),
            valid_until=timezone.now() + datetime.timedelta(days=1),
            min_order_value=100,
            is_active=True,
            max_uses=100,
            used_count=0
        )

        # URL for the API view
        self.url = reverse('apply_coupon')

    def test_apply_coupon_with_spoofed_total(self):
        # Ensure cart is empty
        session = self.client.session
        session['cart'] = {}
        session.save()

        # Send request with a spoofed cart_total of 200 (meeting the min_order_value of 100)
        # The actual cart is empty (total = 0)
        data = {
            'code': 'TEST10',
            'cart_total': 200
        }

        response = self.client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)

        # ASSERTION: The test should fail if the coupon was applied successfully despite the empty cart
        self.assertFalse(response_data.get('success'), "Coupon applied successfully despite empty cart (spoofed total was trusted).")
