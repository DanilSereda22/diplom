# sweetworld/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from store import views as store_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", store_views.index, name="home"),
    path("store/", include("store.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("accounts/", include("users.urls")),  # регистрация, профиль
    path("accounts/", include("django.contrib.auth.urls")),  # login/logout/password
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
