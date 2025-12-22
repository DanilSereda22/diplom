from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .forms import CheckoutForm
from .models import Order, OrderItem
from cart.cart import Cart

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

            order.status = "processing"
            order.save()

            for item in cart:
                if item["quantity"] > item["product"].stock:
                    messages.error(
                        request,
                        f"Недостаточно товара: {item['product'].name}"
                    )
                    order.delete()
                    return redirect("cart:cart_detail")

                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )

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


@transaction.atomic
def payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, status="processing")

    if request.method == "POST":
        for item in order.items.select_related("product"):
            product = item.product

            if item.quantity > product.stock:
                messages.error(
                    request,
                    f"Товар закончился: {product.name}"
                )
                return redirect("cart:cart_detail")

            product.stock -= item.quantity

            if product.stock == 0:
                product.available = False

            product.save()

        order.status = "paid"
        order.save()

        Cart(request).clear()
        return redirect("orders:success", order_id=order.id)

    return render(request, "orders/payment.html", {"order": order})


def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/success.html", {"order": order})
