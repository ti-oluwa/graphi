from django.urls import include, path

from .import views

app_name = "stores"

urlpatterns = [
    path("", views.store_list_view, name="store_list"),
    path("new/", views.store_create_view, name="store_create"),
    path("authorize/", views.store_auth_view, name="store_auth"),
    path("<slug:store_slug>/update/", views.store_update_view, name="store_update"),
    path("<slug:store_slug>/delete/", views.store_delete_view, name="store_delete"),
    path("<slug:store_slug>/products/", include("products.urls", namespace="products")),
    path("<slug:store_slug>/sales/", include("sales.urls", namespace="sales")),
    path("<slug:store_slug>/reports/", include("reports.urls", namespace="reports")),
]
