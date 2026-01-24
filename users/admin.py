# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительно", {"fields": ("phone", "address")}),
    )

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "address",
        "phone",
        "is_staff",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
        "address",
        "phone",
    )
