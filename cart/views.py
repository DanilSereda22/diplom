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
    """
    Универсальная функция добавления/обновления товара.
    Поддерживает обычный POST и AJAX (для модального окна).
    """
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_pk, available=True)
    
    # Получаем данные из запроса
    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1
        
    override = request.POST.get("override") == "true"
    current_qty = cart.get_product_quantity(product)

    # Проверка лимитов товара как в cart.html
    if override:
        if quantity > product.stock:
            quantity = product.stock
            messages.error(request, f"Осталось только {product.stock} шт.")
    else:
        if current_qty + quantity > product.stock:
            quantity = product.stock - current_qty
            if quantity <= 0:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': f'Больше нет в наличии (макс. {product.stock})'}, status=400)
                messages.error(request, f"Осталось только {product.stock} шт.")
                return redirect("cart:cart_detail")

    # Добавляем в корзину
    cart.add(product=product, quantity=quantity, override_quantity=override)

    # Если это AJAX-запрос от нашего нового скрипта
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_total_quantity': len(cart),
            'cart_total_price': float(cart.get_total_price()),
            'product_qty': cart.get_product_quantity(product),
        })

    # Если обычный запрос через форму (например, в корзине)
    return redirect("cart:cart_detail")

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