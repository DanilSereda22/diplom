from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from store.models import Product
from .cart import Cart

def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/cart.html", {"cart": cart})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.add(product=product, quantity=1)
    # возвращаемся на страницу, с которой пришли
    return redirect(request.META.get("HTTP_REFERER", "/"))

@require_POST
def cart_add(request, product_pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_pk, available=True)

    quantity = int(request.POST.get("quantity", 1))
    override = request.POST.get("override") == "true"

    current_qty = cart.get_product_quantity(product)
    
    if override:
        # заменяем количество полностью
        if quantity > product.stock:
            quantity = product.stock
            messages.error(request, f"Осталось только {product.stock} шт.")
    else:
        # добавляем к текущему количеству
        if current_qty + quantity > product.stock:
            quantity = product.stock - current_qty
            if quantity <= 0:
                messages.error(request, f"Осталось только {product.stock} шт.")
                return redirect("cart:cart_detail")

    cart.add(product=product, quantity=quantity, override_quantity=override)
    return redirect("cart:cart_detail")



@require_POST
def cart_remove(request, product_pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_pk)
    cart.remove(product)
    return redirect("cart:cart_detail")
