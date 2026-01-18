from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Product, Vendor, Category, Order, Profile
from decimal import Decimal

@override_settings(AXES_ENABLED=False)
class AutomatedUserJourneyTest(TestCase):
    """
    Automated test simulating a full user journey:
    Register -> Login -> Browse -> Add to Cart -> Checkout
    """

    def setUp(self):
        self.client = Client()
        # Setup catalog
        self.vendor = Vendor.objects.create(name='Flow Vendor', slug='flow-vendor', city='Flow City')
        self.category = Category.objects.create(name='Flow Category', slug='flow-category')
        self.product = Product.objects.create(
            name='Flow Product',
            slug='flow-product',
            price=Decimal('100.00'),
            category=self.category,
            vendor=self.vendor,
            is_active=True,
            stock_quantity=10
        )

    def test_full_purchase_flow(self):
        # 1. Register
        register_url = reverse('signup')
        register_data = {
            'username': 'flow_user',
            'email': 'flow@example.com',
            'password1': 'FlowPass123!',
            'password2': 'FlowPass123!'
        }
        response = self.client.post(register_url, register_data, HTTP_REFERER='http://testserver/signup/')
        self.assertEqual(response.status_code, 302) # Redirect to frontpage

        user = User.objects.get(username='flow_user')
        self.assertTrue(user.is_authenticated)

        # 2. Login (Implicitly logged in after signup, but let's logout and login to be sure)
        self.client.logout()
        login_url = reverse('login')
        login_data = {
            'username': 'flow_user',
            'password': 'FlowPass123!'
        }
        response = self.client.post(login_url, login_data, HTTP_REFERER='http://testserver/login/')
        self.assertEqual(response.status_code, 302) # Redirect to frontpage

        # 3. Browse Product
        product_url = reverse('product_detail', kwargs={'slug': self.product.slug})
        response = self.client.get(product_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Flow Product')

        # 4. Add to Cart
        cart_add_url = reverse('cart_add', kwargs={'product_id': self.product.id})
        response = self.client.post(cart_add_url, HTTP_REFERER=product_url)
        # Should redirect to cart detail
        self.assertEqual(response.status_code, 302)

        # Verify Cart
        cart_url = reverse('cart_detail')
        response = self.client.get(cart_url)
        self.assertContains(response, 'Flow Product')
        self.assertContains(response, '100.00')

        # 5. Checkout
        checkout_url = reverse('checkout')
        checkout_data = {
            'first_name': 'Flow',
            'last_name': 'User',
            'email': 'flow@example.com',
            'address': '123 Flow St',
            'zipcode': '12345',
            'place': 'Flow City',
            'phone': '1234567890'
        }
        # Stripe API keys might be missing, so this might fail if it tries to contact Stripe.
        # But checkout view logic usually creates Order first.
        # If payment_method is COD (default in view if not specified?), it redirects to success.
        # Let's check checkout view logic.
        # It defaults to Stripe if not specified?
        # checkout.html has payment method selection?
        # store/views.py checkout view:
        # if request.method == 'POST':
        #    ...
        #    return redirect('success')

        response = self.client.post(checkout_url, checkout_data, HTTP_REFERER=checkout_url)

        if response.status_code == 302:
            self.assertEqual(response.url, reverse('success'))
            # Verify Order Created
            self.assertTrue(Order.objects.filter(email='flow@example.com').exists())
            order = Order.objects.get(email='flow@example.com')
            self.assertEqual(order.items.count(), 1)
        else:
            # If it failed, print form errors
            if 'form' in response.context:
                print(f"Form Errors: {response.context['form'].errors}")
            else:
                print(f"Checkout Failed with status {response.status_code}")
            self.fail("Checkout failed")
