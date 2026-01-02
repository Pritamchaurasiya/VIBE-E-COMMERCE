from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from store.models import Coupon, Product, Vendor, Category, CartItem
from store.cart import Cart
import json

class SecurityCouponTest(TestCase):
    def setUp(self):
        # Create dependencies
        self.user = User.objects.create_user(username='testuser', password='password')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            price=100.00,
            vendor=self.vendor,
            category=self.category,
            stock_quantity=100
        )

        # Create a coupon
        self.coupon = Coupon.objects.create(
            code='SAVE50',
            discount_type='percent',
            discount_value=50,
            min_order_value=200, # Min order is 200
            max_uses=100,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            is_active=True
        )

        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_apply_coupon_enforces_server_side_total(self):
        """
        Verify that apply_coupon ignores the 'cart_total' sent in request
        and uses the actual server-side calculated total.
        """

        # Populate DB cart for user with 1 item (Total: 100)
        CartItem.objects.create(cart_id=str(self.user.id), product=self.product, quantity=1)

        # Request to apply coupon with FAKE total (250) which would satisfy the min order of 200
        fake_total = 250

        # Test API View
        response = self.client.post(
            '/api/v1/apply-coupon/',
            data=json.dumps({
                'code': 'SAVE50',
                'cart_total': fake_total
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get('success'), "Coupon should fail because actual total (100) < min order (200)")
        self.assertIn('Minimum order value', data.get('error', ''))

        # Test Standard View
        response = self.client.post(
            '/api/apply_coupon/',
            data=json.dumps({
                'code': 'SAVE50',
                'cart_total': fake_total
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get('success'), "Coupon should fail because actual total (100) < min order (200)")
        self.assertIn('Minimum order value', data.get('error', ''))

    def test_apply_coupon_works_with_valid_total(self):
        """
        Verify that apply_coupon works when the actual total meets criteria.
        """
        # Populate DB cart for user with 3 items (Total: 300)
        CartItem.objects.create(cart_id=str(self.user.id), product=self.product, quantity=3)

        response = self.client.post(
            '/api/v1/apply-coupon/',
            data=json.dumps({
                'code': 'SAVE50'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'), "Coupon should apply when actual total (300) >= min order (200)")
        self.assertEqual(data.get('discount_amount'), 150.0) # 50% of 300
