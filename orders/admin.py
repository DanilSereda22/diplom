# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("product", "price", "quantity")
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "phone",
        "delivery_method",
        "status",
        "created_at",
    )
    list_filter = ("status", "delivery_method", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone")
    inlines = [OrderItemInline]

