from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout_view, name="checkout"),
    path("payment/<int:order_id>/", views.payment, name="payment"),
    path("success/<int:order_id>/", views.order_success_view, name="order_success"),
    path('order/delete/<int:order_id>/', views.order_delete, name='order_delete'),

    path("courier/", views.courier_orders_view, name="courier_orders"),
    path("courier/complete/<int:order_id>/", views.complete_delivery_view, name="complete_delivery"),

    path("admin/orders/", views.admin_orders_view, name="admin_orders"),
    path("admin/orders/edit/<int:order_id>/", views.admin_edit_order, name="admin_edit_order"),
    path("admin/orders/item/update/<int:item_id>/", views.admin_update_item, name="admin_update_item"),
    path("admin/orders/item/delete/<int:item_id>/", views.admin_delete_item, name="admin_delete_item"),
    path("admin/orders/item/add/<int:order_id>/", views.admin_add_item, name="admin_add_item"),
    path("admin/delete/<int:order_id>/", views.admin_delete_order, name="admin_delete_order"),
]
