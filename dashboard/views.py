from django.views import generic
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from typing import Any, Dict
import json
from django.utils import timezone

from stores.utils import get_stores_count, parse_timeframe_statement
from stores.models import Store
from products.utils import get_products_count
from products.models import Product
from sales.utils import aggregate_sales_count, aggregate_revenue_from_sales
from products.models import ProductCategory
from .utils import get_most_sold_product, get_most_active_store



class DashboardView(LoginRequiredMixin, generic.TemplateView):
    """View for the user dashboard."""
    template_name = "dashboard/dashboard.html"
    http_method_names = ["get"]

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["stores_count"] = get_stores_count(self.request.user)
        context["products_count"] = get_products_count(self.request.user)
        todays_date_for_user = self.request.user.to_local_timezone(timezone.now()).date()
        context["sales_count_today"] = aggregate_sales_count(self.request.user, date=todays_date_for_user)
        context["revenue_from_sales_today"] = aggregate_revenue_from_sales(self.request.user, date=todays_date_for_user)
        context["product_categories"] = ProductCategory.labels
        context["most_sold_product"] = get_most_sold_product(Product.objects.filter(store__owner=self.request.user))
        context["most_active_store"] = get_most_active_store(Store.objects.filter(owner=self.request.user))
        return context
    


class SalesRevenueStatsView(LoginRequiredMixin, generic.View):
    """View for retrieving sale and revenue statistics in dashboard"""
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        stat_type = data.pop("statType", None)

        if stat_type == "sales":
            result = aggregate_sales_count(self.request.user, **data)
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Sales statistics retrieved successfully!",
                    "data": {
                        "result": result
                    }
                },
                status=200
            )
        
        elif stat_type == "revenue":
            result = aggregate_revenue_from_sales(self.request.user, **data)
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Revenue statistics retrieved successfully!",
                    "data": {
                        "result": f'{result.currency}{result.amount:,}'
                    }
                },
                status=200
            )
        
        return JsonResponse(
            data={
                "status": "error",
                "detail": f"Invalid statistics type: {stat_type}"
            },
            status=400
        )



class MostSoldProductStatsView(LoginRequiredMixin, generic.View):
    """View for retrieving most sold product statistics in dashboard"""
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        timeframe: str = data.get("timeframe")
        if timeframe.lower() == "all time":
            timeframe = None
        else:
            timeframe = parse_timeframe_statement(timeframe)

        products = Product.objects.filter(store__owner=request.user)
        sales_filters = {}
        if timeframe:
            sales_filters={"made_at__range": timeframe}
        most_sold_product = get_most_sold_product(products, sales_filters)

        if most_sold_product:
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Most sold product statistics retrieved successfully!",
                    "data": {
                        "mostSoldProduct": {
                            "name": most_sold_product.name,
                            "salesCount": most_sold_product.sales_count,
                            "store": most_sold_product.store.name,
                        }
                    }
                },
                status=200
            )
        
        return JsonResponse(
            data={
                "status": "success",
                "detail": "No sales recorded in the given timeframe",
                "data": {
                    "mostSoldProduct": None
                }
            },
            status=200
        )



class MostActiveStoreStatsView(LoginRequiredMixin, generic.View):
    """View for retrieving most active store statistics in dashboard"""
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        timeframe: str = data.get("timeframe")
        if timeframe.lower() == "all time":
            timeframe = None
        else:
            timeframe = parse_timeframe_statement(timeframe)

        stores = Store.objects.filter(owner=request.user)
        sales_filters = {}
        if timeframe:
            sales_filters={"made_at__range": timeframe}
        most_active_store = get_most_active_store(stores, sales_filters)

        if most_active_store:
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Most active store statistics retrieved successfully!",
                    "data": {
                        "mostActiveStore": {
                            "name": most_active_store.name,
                            "salesCount": most_active_store.sales_count,
                        }
                    }
                },
                status=200
            )
        
        return JsonResponse(
            data={
                "status": "success",
                "detail": "No store activity recorded in the given timeframe",
                "data": {
                    "mostActiveStore": None
                }
            },
            status=200
        )


dashboard_view = DashboardView.as_view()
sales_revenue_stats_view = SalesRevenueStatsView.as_view()
most_sold_product_stat_view = MostSoldProductStatsView.as_view()
most_active_store_stat_view = MostActiveStoreStatsView.as_view()
