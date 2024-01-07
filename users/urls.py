from django.urls import path

from . import views


urlpatterns = [
    path("signup/", views.user_create_view, name="signup"),
    path("signin/", views.user_auth_view, name="signin"),
]
