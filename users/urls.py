from django.urls import path

from . import views


urlpatterns = [
    path("", views.user_dashboard_view, name="dashboard"),
    path("signup/", views.user_create_view, name="signup"),
    path("signin/", views.user_auth_view, name="signin"),
    path("signout/", views.user_logout_view, name="signout"),
    path("verification/<str:token>/", views.user_verification_view, name="verification"),
]
