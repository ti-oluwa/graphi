from django.urls import path

from . import views

app_name = "sales"


urlpatterns = [
    path("", views.sale_list_view, name="sale_list"),
    path("new/", views.sale_add_view, name="sale_add"),
    path("<str:sale_id>/update/", views.sale_update_view, name="sale_update"),
    path("<str:sale_id>/delete/", views.sale_delete_view, name="sale_delete")
]
