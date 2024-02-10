from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.index_view, name="index"),
    path("accounts/", include("users.urls", namespace="users")),
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
    path("stores/", include("stores.urls", namespace="stores")),
]
