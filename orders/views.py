from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order, OrderItem
from store.models import Product
from .forms import CheckoutForm
from cart.cart import Cart
from django.views.decorators.http import require_POST
from django.db import transaction

def is_courier(user):
    return user.is_staff


def is_admin(user):
    return user.is_authenticated and user.is_superuser

# ОФОРМЛЕНИЕ ЗАКАЗА
@login_required(login_url='users:login')  # редирект на страницу логина
def checkout_view(request):
    cart = Cart(request)
    if cart.is_empty():
        messages.info(request, "Ваша корзина пуста.")
        return redirect("store:product_list")

    initial = {
        "first_name": getattr(request.user, "first_name", ""),
        "last_name": getattr(request.user, "last_name", ""),
        "email": getattr(request.user, "email", ""),
        "phone": getattr(request.user, "phone", ""),
        "delivery_address": getattr(request.user, "address", ""),
    }

    if request.method == "POST":
        form = CheckoutForm(request.POST, initial=initial)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user

            # СПИСАНИЕ БОНУСОВ
            use_bonus = Decimal(request.POST.get("use_bonus") or 0)
            use_bonus = min(use_bonus, 350, request.user.bonus_points)
            order.bonus_used = use_bonus
            request.user.bonus_points -= use_bonus
            request.user.save()

            order.status = "processing"
            order.save()
            # ДОБАВЛЕНИЕ ТОВАРОВ
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"]
                )

            request.session["order_id"] = order.id
            return redirect("orders:payment", order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, "orders/checkout.html", {"form": form, "cart": cart, "user": request.user})

# ОПЛАТА ЗАКАЗА
@login_required(login_url='users:login')
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        for item in order.items.select_related("product"):
            product = item.product
            if item.quantity > product.stock:
                messages.error(request, f"Товар закончился: {product.name}")
                return redirect("cart:cart_detail")
            product.stock -= item.quantity
            if product.stock <= 0:
                product.available = False
            product.save()

        order.status = "paid"
        order.save()

        # Начисляем 1% бонусов
        bonus = order.total_price - order.bonus_used
        request.user.bonus_points += bonus * Decimal("0.01")
        request.user.save()

        # Очистка корзины
        Cart(request).clear()
        request.session.modified = True

        return redirect("orders:order_success", order_id=order.id)

    return render(request, "orders/payment.html", {"order": order})

# СТРАНИЦА УСПЕШНОГО ЗАКАЗА
@login_required(login_url='users:login')
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    bonus_added = getattr(request.session, "bonus_added", None)
    if bonus_added is None:
        bonus_added = (order.total_price - order.bonus_used) * Decimal("0.01")
    return render(request, "orders/success.html", {
        "order": order,
        "bonus_added": bonus_added
    })
@login_required
@require_POST
def order_delete(request, order_id):
    with transaction.atomic():
        # Находим заказ (только статус processing, чтобы нельзя было удалить уже оплаченный)
        order = get_object_or_404(Order, id=order_id, user=request.user, status='processing')
        
        # 1. ВОЗВРАТ БОНУСОВ (если они физически списались при создании заказа)
        if order.bonus_used > 0:
            user = request.user
            user.bonus_points += order.bonus_used
            user.save()
        
        # 2. ПРОСТО УДАЛЯЕМ ЗАКАЗ (склад не трогаем, так как списания не было)
        order.delete()
        
        messages.success(request, "Заказ успешно отменен и удален.")
            
    return redirect('users:profile')

# КУРЬЕР
@login_required(login_url='users:login')
@user_passes_test(is_courier)
def courier_orders_view(request):
    orders = Order.objects.filter(delivery_method="delivery", status="paid").order_by("-created_at")
    return render(request, "orders/courier_orders.html", {"orders": orders})


@staff_member_required
def complete_delivery_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, delivery_method="delivery", status="paid")
    order.status = "delivered"
    order.save()
    return redirect("orders:courier_orders")

# АДМИНКА
@user_passes_test(is_admin)
def admin_orders_view(request):
    orders = Order.objects.all().prefetch_related("items__product").order_by("-created_at")
    return render(request, "orders/admin_orders.html", {"orders": orders})


@user_passes_test(is_admin)
def admin_update_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)
    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save()
        if status == "paid" and order.user:
            bonus = order.total_price - order.bonus_used
            order.user.bonus_points += bonus * Decimal("0.01")
            order.user.save()
    return redirect("orders:admin_orders")


@user_passes_test(is_admin)
def admin_delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect("orders:admin_orders")


@user_passes_test(is_admin)
def admin_edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    products = Product.objects.filter(available=True)

    if request.method == "POST":
        for field in [
            "first_name", "last_name", "email", "phone",
            "delivery_method", "delivery_address",
            "delivery_comment", "status"
        ]:
            setattr(order, field, request.POST.get(field))

        order.save()

        # ✅ ВАЖНО: редирект после сохранения
        return redirect("orders:admin_orders")

    return render(request, "orders/admin_edit_order.html", {
        "order": order,
        "products": products
    })


@user_passes_test(is_admin)
def admin_update_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    item.quantity = int(request.POST.get("quantity", 1))
    item.save()
    return redirect("orders:admin_edit_order", item.order.id)


@user_passes_test(is_admin)
def admin_delete_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    order_id = item.order.id
    item.delete()
    return redirect("orders:admin_edit_order", order_id)


@user_passes_test(lambda u: u.is_staff)
def admin_add_item(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        product = get_object_or_404(Product, id=request.POST.get("product_id"))
        quantity = int(request.POST.get("quantity", 1))

        # Используем твое свойство из модели Product для получения цены
        price = product.final_price

        OrderItem.objects.create(
            order=order, 
            product=product, 
            price=price, 
            quantity=quantity
        )
        
        # Сохраняем заказ для пересчета итогов
        order.save() 
        
    return redirect("orders:admin_edit_order", order.id)