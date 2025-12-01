# apps/orders/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CheckoutForm
from .models import Order, OrderItem
from cart.cart import Cart
from django.contrib.auth import get_user_model

User = get_user_model()

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
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
            cart.clear()
            messages.success(request, f"Спасибо! Заказ #{order.pk} создан.")
            return redirect("store:product_list")
    else:
        if request.user.is_authenticated:
            initial = {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": getattr(request.user, "phone", ""),
                "address": getattr(request.user, "address", ""),
            }
            form = CheckoutForm(initial=initial)
        else:
            form = CheckoutForm()
    return render(request, "orders/checkout.html", {"form": form, "cart": cart})
