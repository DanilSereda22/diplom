# apps/orders/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .forms import CheckoutForm
from .models import Order, OrderItem
from cart.cart import Cart

def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/success.html", {"order": order})

def payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        order.status = "paid"
        order.save()

        Cart(request).clear()

        return redirect("orders:success", order_id=order.id)

    return render(request, "orders/payment.html", {"order": order})

def checkout_view(request):
    cart = Cart(request)

    if cart.is_empty():
        messages.info(request, "Ваша корзина пуста.")
        return redirect("store:product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)

            if request.user.is_authenticated:
                order.user = request.user

            order.status = "processing"  # ⬅️ важно
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )

            # ❌ НЕ очищаем корзину здесь
            # ❌ НЕ редиректим в магазин

            return redirect("orders:payment", order_id=order.id)

    else:
        if request.user.is_authenticated:
            form = CheckoutForm(initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": getattr(request.user, "phone", ""),
            })
        else:
            form = CheckoutForm()

    return render(request, "orders/checkout.html", {
        "form": form,
        "cart": cart
    })
