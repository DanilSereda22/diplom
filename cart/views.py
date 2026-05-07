from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse # Импортируем для работы с AJAX
from store.models import Product
from .cart import Cart
from decimal import Decimal
from orders.models import *

def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart/cart.html", {"cart": cart})

@require_POST
def cart_add(request, product_pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_pk, available=True)
    
    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1
        
    override = request.POST.get("override") == "true"
    current_qty = cart.get_product_quantity(product)

    # Логика проверки остатков
    if override:
        if quantity > product.stock: quantity = product.stock
    else:
        if current_qty + quantity > product.stock:
            quantity = product.stock - current_qty

    if quantity > 0 or override:
        cart.add(product=product, quantity=quantity, override_quantity=override)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_total_quantity': len(cart),
            'cart_total_price': float(cart.get_total_price()),
            'product_qty': cart.get_product_quantity(product),
        })

    return redirect("cart:cart_detail")

def checkout(request):
    cart = Cart(request)
    if cart.is_empty():
        return redirect("store:home")

    user = request.user if request.user.is_authenticated else None

    if request.method == "POST":
        total = cart.get_total_price()
        
        # Логика бонусов
        used_bonus = Decimal(request.POST.get("use_bonus", 0))
        if user and used_bonus > 0:
            used_bonus = min(used_bonus, user.bonus_points, total * Decimal('0.5')) # Например, макс 50% бонусами
            total -= used_bonus
            user.bonus_points -= used_bonus
            user.save()

        # Создаем заказ
        order = Order.objects.create(
            user=user,
            total_price=total,
            status="processing"
        )

        # КЛЮЧЕВОЙ МОМЕНТ: Берем цену из 'item', так как там она со скидкой
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price=item["price"]  # Это цена из корзины (уже со скидкой!)
            )

        cart.clear()
        return redirect("orders:order_success", order_id=order.id)

    return render(request, "cart/checkout.html", {"cart": cart, "user": user})

def add_to_cart(request, product_id):
    """
    Функция для кнопки '+' в каталоге.
    Теперь она перенаправляет на cart_add для единой логики.
    """
    return cart_add(request, product_id)

@require_POST
def cart_remove(request, product_pk):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_pk)
    cart.remove(product)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'cart_total_quantity': len(cart),
            'cart_total_price': float(cart.get_total_price()),
        })
        
    return redirect("cart:cart_detail")

@require_POST
def cart_clear(request):
    cart = Cart(request)
    cart.clear()

    # Поддержка AJAX (в твоём стиле)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'cart_total_quantity': 0,
            'cart_total_price': 0,
        })

    messages.success(request, "Корзина очищена 🗑️")
    return redirect("cart:cart_detail")