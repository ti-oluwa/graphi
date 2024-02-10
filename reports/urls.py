from django.urls import path

from . import views

app_name = "reports"


urlpatterns = [
    path("sales/", views.sales_report_view, name="sales_report"),
]
