from django.urls import path

from .import views

app_name = "stores"

urlpatterns = [
    path("", views.store_list_view, name="store_list"),
    path("new/", views.store_create_view, name="store_create"),
    path("authorize/", views.store_auth_view, name="store_auth"),
    path("<uuid:store_id>/update/", views.store_update_view, name="store_update"),
    path("<uuid:store_id>/delete/", views.store_delete_view, name="store_delete"),
]
