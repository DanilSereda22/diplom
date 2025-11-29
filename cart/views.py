# apps/cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from store.models import Product
from .cart import Cart

def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/cart.html", {"cart": cart})

@require_POST
def cart_add(request, product_pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_pk)
    quantity = int(request.POST.get("quantity", 1))
    override = request.POST.get("override", "false") == "true"
    cart.add(product=product, quantity=quantity, override_quantity=override)
    return redirect("cart:cart_detail")

@require_POST
def cart_remove(request, product_pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_pk)
    cart.remove(product)
    return redirect("cart:cart_detail")
