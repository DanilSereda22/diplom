# users/urls.py
from django.urls import path, reverse_lazy
from . import views
from .forms import CustomPasswordResetForm
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from .views import CustomLoginView

app_name = "users"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("register/", views.register_view, name="register"),
    path("profile/", views.profile_view, name="profile"),
    path("password-reset/", PasswordResetView.as_view(
        template_name="users/password_reset.html",
        email_template_name="users/password_reset_email.txt",
        html_email_template_name="users/password_reset_email.html",
        subject_template_name="users/password_reset_subject.txt",
        success_url=reverse_lazy("users:password_reset_done"),
        form_class=CustomPasswordResetForm,), name="password_reset"),
    path("password-reset/done/", PasswordResetDoneView.as_view(template_name="users/password_reset_done.html",), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(
        template_name="users/password_reset_confirm.html",
        success_url=reverse_lazy("users:password_reset_complete"),), name="password_reset_confirm"),
    path("reset/done/", PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html",), name="password_reset_complete"),
]
