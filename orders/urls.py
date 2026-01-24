# orders/urls.py
from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path("payment/<int:order_id>/", views.payment_view, name="payment"),
    path("success/<int:order_id>/", views.order_success_view, name="success"),
    
]
