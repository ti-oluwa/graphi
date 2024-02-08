from django.urls import path

from . import views

app_name = "dashboard"


urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("stats/advanced-options/", views.dashboard_stats_view, name="dashboard_stats"),
]
