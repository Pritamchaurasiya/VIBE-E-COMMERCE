import os
import django
from django.conf import settings

# Configure settings manually if not already configured
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.test import RequestFactory, TestCase
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from store.models import Product, Category, Vendor, Coupon, Order
from store.api_views import StartOrderView, ApplyCouponView
from store.cart import Cart
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class OrderFlowTest(TestCase):
    def setUp(self):
        # Setup data
        self.vendor = Vendor.objects.create(name="Test Vendor", slug="test-vendor")
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            price=Decimal("100.00"),
            stock_quantity=10,
            vendor=self.vendor,
            category=self.category,
            is_active=True
        )

        self.coupon = Coupon.objects.create(
            code="TEST10",
            discount_type="percent",
            discount_value=Decimal("10.00"),
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
            is_active=True,
            max_uses=10
        )

        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')

    def add_session(self, request):
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_full_order_flow_with_coupon(self):
        # 1. Add item to cart
        # Since Cart uses session, we need to simulate session persistence

        # Create request for ApplyCoupon
        request_coupon = self.factory.post('/api/apply-coupon/', {
            'code': 'TEST10',
            'cart_total': 100
        }, content_type='application/json')
        # Disable CSRF for test
        request_coupon._dont_enforce_csrf_checks = True
        # Add user to request
        request_coupon.user = self.user
        self.add_session(request_coupon)

        # Initialize cart in this session
        cart = Cart(request_coupon)
        cart.add(self.product.id, 1)

        # 2. Apply Coupon
        view_coupon = ApplyCouponView.as_view()
        response_coupon = view_coupon(request_coupon)

        print("Apply Coupon Response:", response_coupon.data)
        self.assertTrue(response_coupon.data['success'])
        self.assertEqual(request_coupon.session.get('coupon_id'), self.coupon.id)

        # 3. Place Order
        request_order = self.factory.post('/api/start-order/', {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'address': '123 St',
            'zipcode': '12345',
            'place': 'City',
            'phone': '1234567890',
            'payment_method': 'cod'
        }, content_type='application/json')

        # Disable CSRF for test
        request_order._dont_enforce_csrf_checks = True

        # Share session
        request_order.session = request_coupon.session
        request_order.user = self.user

        view_order = StartOrderView.as_view()
        response_order = view_order(request_order)

        print("Start Order Response:", response_order.data)

        if 'error' in response_order.data:
            self.fail(f"Order failed: {response_order.data['error']}")

        order_id = response_order.data['order_id']
        order = Order.objects.get(id=order_id)

        # Verify
        self.assertEqual(order.coupon, self.coupon)
        # Total should be 100 - 10% = 90
        self.assertEqual(order.paid_amount, Decimal("90.00"))
        self.assertEqual(order.discount_amount, Decimal("10.00"))

        # Verify stock
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 9)

        print("Test Passed: Order created with coupon and stock decremented.")

if __name__ == '__main__':
    # Run the test
    try:
        from django.test.runner import DiscoverRunner
        runner = DiscoverRunner(verbosity=2)
        failures = runner.run_tests(['test_flow_fixed'])
        if failures:
            print("Tests Failed")
            exit(1)
        else:
            print("All Tests Passed")
            exit(0)
    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()
