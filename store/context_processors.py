"""
Context processors for the store app.
"""
from .cart import Cart

def cart(request):
    """
    Context processor to make the cart available globally in templates.
    """
    cart_obj = Cart(request)
    return {
        'cart': cart_obj,
        'cart_item_count': len(cart_obj),
        'cart_total_cost': cart_obj.get_total_cost() 
    }
