"""
Cart management module.
"""
from django.conf import settings

from .models import Product

class Cart(object):
    """
    Cart class to manage the shopping cart in the session.
    """
    def __init__(self, request):
        self.session = request.session
        cart_session = self.session.get(settings.CART_SESSION_ID)

        if not cart_session:
            cart_session = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart_data = cart_session

        if any(not isinstance(value, dict) for value in self.cart_data.values()):
            self.cart_data = {
                key: ({'quantity': value, 'id': key} if not isinstance(value, dict) else value)
                for key, value in self.cart_data.items()
            }
            self.save()
    
    def __iter__(self):
        product_ids = self.cart_data.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        cart_data_copy = self.cart_data.copy()

        for product in products:
            cart_data_copy[str(product.id)]['product'] = product
        
        for item in cart_data_copy.values():
            if 'product' in item:
                item['total_price'] = item['product'].price * item['quantity']
                yield item
    
    def __len__(self):
        return sum(item['quantity'] for item in self.cart_data.values())
    
    def save(self):
        """
        Mark the session as modified to ensure it gets saved.
        """
        self.session[settings.CART_SESSION_ID] = self.cart_data
        self.session.modified = True
    
    def add(self, product_id, quantity=1, update_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product_id)

        if product_id not in self.cart_data:
            self.cart_data[product_id] = {'quantity': 0, 'id': product_id}
        
        if update_quantity:
            self.cart_data[product_id]['quantity'] += int(quantity)
        else:
            self.cart_data[product_id]['quantity'] += 1

        if self.cart_data[product_id]['quantity'] == 0:
            self.remove(product_id)
        
        self.save()
    
    def remove(self, product_id):
        """
        Remove a product from the cart.
        """
        if product_id in self.cart_data:
            del self.cart_data[product_id]
            self.save()
    
    def clear(self):
        """
        Remove the cart from the session.
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
    
    def get_total_cost(self):
        """
        Calculate the total cost of items in the cart.
        """
        product_ids = self.cart_data.keys()
        products = Product.objects.filter(id__in=product_ids)

        return sum(product.price * self.cart_data[str(product.id)]['quantity'] for product in products)