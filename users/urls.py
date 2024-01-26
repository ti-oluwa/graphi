from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # User authentication URLs
    path("signup/", views.user_create_view, name="signup"),
    path("signin/", views.user_login_view, name="signin"),
    path("signout/", views.user_logout_view, name="signout"),
    path("account-verification/<str:token>/", views.user_verification_view, name="account_verification"),
    path("password-verification/", views.password_verification_view, name="password_verification"),
    
    # Dashboard URLs
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("dashboard/stats/advanced-options/", views.dashboard_stats_view, name="dashboard_stats"),
]
