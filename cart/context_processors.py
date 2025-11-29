# apps/cart/context_processors.py
from .cart import Cart

def cart_counter(request):
    cart = Cart(request)
    return {"cart_counter": len(cart)}
