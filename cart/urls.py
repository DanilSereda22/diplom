# apps/cart/urls.py
from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="cart_detail"),
    path("add/<int:product_pk>/", views.cart_add, name="cart_add"),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove/<int:product_pk>/", views.cart_remove, name="cart_remove"),
    path("clear/", views.cart_clear, name="cart_clear"),

]
