from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from store.models import Product
from .cart import Cart
from decimal import Decimal
from orders.models import *
def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/cart.html", {"cart": cart})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.add(product=product, quantity=1)
    return redirect(request.META.get("HTTP_REFERER", "/"))

@require_POST
def cart_add(request, product_pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_pk, available=True)
    quantity = int(request.POST.get("quantity", 1))
    override = request.POST.get("override") == "true"
    current_qty = cart.get_product_quantity(product)

    if override:
        if quantity > product.stock:
            quantity = product.stock
            messages.error(request, f"Осталось только {product.stock} шт.")
    else:
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

def checkout(request):
    cart = Cart(request)
    user = request.user if request.user.is_authenticated else None

    if request.method == "POST":
        used_bonus = Decimal(request.POST.get("use_bonus", 0))
        total = cart.get_total_price()

        # Списание бонусов
        if user and used_bonus > 0:
            used_bonus = min(used_bonus, user.bonus_points, total)
            total -= used_bonus
            user.bonus_points -= used_bonus
            user.save()

        # Создание заказа
        order = Order.objects.create(
            user=user,
            total_price=total,
            status="processing",
            # ... остальные поля
        )

        # Добавление товаров в заказ
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price=item["price"],
            )

        # Очистка корзины
        cart.clear()

        return redirect("orders:order_success", order_id=order.id)

    return render(request, "cart/checkout.html", {"cart": cart, "user": user})
