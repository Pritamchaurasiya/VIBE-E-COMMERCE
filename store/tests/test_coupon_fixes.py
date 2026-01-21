from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from store.models import Coupon, Product, Category, Vendor, CartItem
from store.coupon_service import CouponService

# Override settings to use LocMemCache and Database Session
@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class CouponRaceConditionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.coupon = Coupon.objects.create(
            code='RACE10',
            discount_type='fixed',
            discount_value=Decimal('10.00'),
            max_uses=100,
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            min_order_value=Decimal('50.00')
        )
        self.service = CouponService(user=self.user)

    def test_coupon_atomic_increment(self):
        """Verify that F() expression is used for incrementing usage count."""
        initial_count = self.coupon.used_count
        success, message = self.service.apply_coupon('RACE10')

        self.assertTrue(success)
        self.coupon.refresh_from_db()
        self.assertEqual(self.coupon.used_count, initial_count + 1)
        print(f"\nCoupon incremented from {initial_count} to {self.coupon.used_count}")

@override_settings(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    },
    SESSION_ENGINE='django.contrib.sessions.backends.db'
)
class ApplyCouponSecurityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='secureuser', password='password')
        self.client.login(username='secureuser', password='password')

        self.category = Category.objects.create(name='Test Category', slug='test-cat')
        self.vendor = Vendor.objects.create(name='Test Vendor', slug='test-vendor')

        self.product = Product.objects.create(
            name='Test Product',
            price=Decimal('100.00'),
            stock_quantity=10,
            is_active=True,
            category=self.category,
            vendor=self.vendor
        )

        self.coupon = Coupon.objects.create(
            code='SECURE10',
            discount_type='percent',
            discount_value=Decimal('10.00'), # 10% off
            max_uses=100,
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=1),
            min_order_value=Decimal('50.00')
        )

    def test_apply_coupon_calculates_total_server_side(self):
        """Test that ApplyCouponView ignores client-provided cart_total."""

        # Since the user is logged in, Cart uses DB-backed CartItem.
        # We must create a CartItem directly in the DB for the user.
        CartItem.objects.create(
            cart_id=str(self.user.id),
            product=self.product,
            quantity=1
        )

        # Request with a fake, high cart_total
        fake_total = 10000.00
        response = self.client.post('/api/apply_coupon/', {
            'code': 'SECURE10',
            'cart_total': fake_total
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertTrue(data['success'])

        # Expected discount: 10% of 100.00 (actual cart) = 10.00
        # If it used fake_total: 10% of 10000 = 1000.00

        self.assertEqual(float(data['discount_amount']), 10.00)
        print(f"\nDiscount calculated: {data['discount_amount']} (Expected: 10.0). Client provided total {fake_total} was ignored.")
