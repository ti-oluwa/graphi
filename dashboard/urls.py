from django.urls import path

from . import views

app_name = "dashboard"


urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("stats/sales-revenue/", views.sales_revenue_stats_view, name="sales_revenue_stats"),
    path("stats/most-sold-product/", views.most_sold_product_stat_view, name="most_sold_product_stat"),
    path("stats/most-active-store/", views.most_active_store_stat_view, name="most_active_store_stat"),
]
