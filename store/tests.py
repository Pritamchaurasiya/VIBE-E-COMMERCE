from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.models import User
from store.models import Product, Category
from store.cart import Cart

class CartTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product1 = Product.objects.create(category=self.category, name='Test Product 1', slug='test-product-1', price=10.00)
        self.product2 = Product.objects.create(category=self.category, name='Test Product 2', slug='test-product-2', price=20.00)

    def _get_request_with_session(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_add_to_cart(self):
        request = self._get_request_with_session()
        cart = Cart(request)
        
        cart.add(product_id=self.product1.id)
        self.assertEqual(len(cart), 1)
        
        cart.add(product_id=self.product1.id)
        self.assertEqual(len(cart), 2)
        
        cart.add(product_id=self.product2.id)
        self.assertEqual(len(cart), 3)

        self.assertEqual(cart.get_total_cost(), 40.00)

    def test_update_cart(self):
        request = self._get_request_with_session()
        cart = Cart(request)
        cart.add(product_id=self.product1.id)
        cart.add(product_id=self.product1.id)
        
        cart.add(product_id=self.product1.id, quantity=-1, update_quantity=True)
        self.assertEqual(len(cart), 1)

        cart.add(product_id=self.product1.id, quantity=5, update_quantity=True)
        self.assertEqual(len(cart), 6)

    def test_remove_from_cart(self):
        request = self._get_request_with_session()
        cart = Cart(request)
        cart.add(product_id=self.product1.id)
        self.assertEqual(len(cart), 1)
        
        cart.remove(product_id=self.product1.id)
        self.assertEqual(len(cart), 0)

    def test_cart_migration(self):
        # Simulate old cart data
        request = self._get_request_with_session()
        session = request.session
        session['cart_session_id'] = {str(self.product1.id): 2}
        session.save()
        
        cart = Cart(request)
        self.assertEqual(len(cart), 2)
        self.assertEqual(cart.get_total_cost(), 20.00)

        # Check if it has been migrated to the new format
        self.assertIsInstance(cart.cart[str(self.product1.id)], dict)
        self.assertEqual(cart.cart[str(self.product1.id)]['quantity'], 2)