from django.urls import path

from . import views


urlpatterns = [
    # User authentication URLs
    path("signup/", views.user_create_view, name="signup"),
    path("signin/", views.user_auth_view, name="signin"),
    path("signout/", views.user_logout_view, name="signout"),
    path("verification/<str:token>/", views.user_verification_view, name="verification"),
    
    # Dashboard URLs
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("dashboard/stats/advanced-options/", views.dashboard_stats_view, name="dashboard-stats"),
]
