from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required,user_passes_test
from .forms import CheckoutForm
from .models import Order, OrderItem,Product
from cart.cart import Cart
from django.contrib.admin.views.decorators import staff_member_required

def is_courier(user):
    return user.is_staff

@login_required
@user_passes_test(is_courier)
def courier_orders(request):
    orders = Order.objects.filter(
        delivery_method='delivery',
        status='paid'
    ).order_by('-created_at')

    return render(request, 'orders/courier_orders.html', {
        'orders': orders
    })
@staff_member_required
def complete_delivery_view(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        delivery_method="delivery",
        status="paid"
    )

    order.status = "delivered"
    order.save()

    return redirect("orders:courier_orders")

@staff_member_required(login_url="login")
def courier_orders_view(request):
    orders = Order.objects.filter(
        delivery_method="delivery",
        status="paid"
    ).order_by("-created_at")

    return render(request, "orders/courier_orders.html", {
        "orders": orders
    })
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
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    price=item["price"],
                    quantity=item["quantity"],
                )

            return redirect("orders:payment", order_id=order.id)
    else:
        initial = {}

        if request.user.is_authenticated:
            initial = {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": getattr(request.user, "phone", ""),
                "delivery_address": getattr(request.user, "address", ""),
            }

        form = CheckoutForm(initial=initial)

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

    return render(request, "orders/payment.html", {
        "order": order
    })


def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "orders/success.html", {
        "order": order
    })


## Админка
def is_admin(user):
    return user.is_authenticated and user.is_staff

from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def admin_delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return redirect("orders:admin_orders")

@user_passes_test(is_admin)
def admin_orders_view(request):
    orders = Order.objects.all().prefetch_related("items__product").order_by("-created_at")

    return render(request, "orders/admin_orders.html", {
        "orders": orders
    })

@user_passes_test(is_admin)
def admin_update_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)

    if status in dict(Order.STATUS_CHOICES):
        order.status = status
        order.save()

    return redirect("orders:admin_orders")


@user_passes_test(lambda u: u.is_superuser)
def admin_edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        for field in [
            "first_name", "last_name", "email", "phone",
            "delivery_method", "delivery_address",
            "delivery_comment", "status"
        ]:
            setattr(order, field, request.POST.get(field))
        order.save()

    products = Product.objects.filter(available=True)

    return render(request, "orders/admin_edit_order.html", {
        "order": order,
        "products": products
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_update_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    item.quantity = int(request.POST.get("quantity", 1))
    item.save()
    return redirect("orders:admin_edit_order", item.order.id)


@user_passes_test(lambda u: u.is_superuser)
def admin_delete_item(request, item_id):
    if request.method != "POST":
        return redirect("orders:admin_orders")

    item = get_object_or_404(OrderItem, id=item_id)
    order_id = item.order_id
    item.delete()

    return redirect("orders:admin_edit_order", order_id)




@user_passes_test(lambda u: u.is_superuser)
def admin_add_item(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    product = get_object_or_404(Product, id=request.POST["product_id"])

    OrderItem.objects.create(
        order=order,
        product=product,
        price=product.price,
        quantity=int(request.POST.get("quantity", 1))
    )
    return redirect("orders:admin_edit_order", order.id)
