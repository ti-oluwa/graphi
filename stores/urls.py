from django.urls import path

from .import views

app_name = "stores"

urlpatterns = [
    path("", views.store_list_view, name="store_list"),
    path("new/", views.store_create_view, name="store_create"),
    path("<uuid:store_id>/update/", views.store_update_view, name="store_update"),
]
