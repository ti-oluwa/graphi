from django.urls import path

from .import views


app_name = "products"

urlpatterns = [
    path("", views.product_list_view, name="product_list"),
    path("new/", views.product_add_view, name="product_add"),
    path("<uuid:product_id>/update/", views.product_update_view, name="product_update"),
    path("<uuid:product_id>/delete/", views.product_delete_view, name="product_delete"),
]
