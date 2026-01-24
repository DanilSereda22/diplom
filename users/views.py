# users/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.views import LoginView
from .models import CustomUser

class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return "/users/admin/dashboard/"
        if user.is_staff:
            return "/orders/courier/"
        return "/users/profile/"

def profile_redirect(request):
    if request.user.is_staff:
        return redirect("orders:courier_orders")
    return redirect("users:profile")

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "users/register.html", {"form": form})

@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.phone = request.POST.get("phone", user.phone)
        user.address = request.POST.get("address", user.address)
        user.save()
        return redirect("users:profile")
    return render(request, "users/profile.html", {"user": user})

## Админка

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, "admin/dashboard.html")

@user_passes_test(is_admin)
def admin_users_view(request):
    users = CustomUser.objects.all().order_by("-date_joined")
    return render(request, "users/admin_users.html", {
        "users": users
    })

@user_passes_test(is_admin)
def admin_edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        user.username = request.POST.get("username")
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.phone = request.POST.get("phone")
        user.address = request.POST.get("address")
        user.is_staff = bool(request.POST.get("is_staff"))
        user.is_superuser = bool(request.POST.get("is_superuser"))
        user.save()
        return redirect("users:admin_users")
    return render(request, "users/admin_edit_user.html", {
        "user_obj": user
    })

@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        user.delete()
    return redirect("users:admin_users")

@user_passes_test(is_admin)
def admin_add_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:admin_users")
    else:
        form = RegisterForm()
    return render(request, "users/admin_add_user.html", {
        "form": form
    })
