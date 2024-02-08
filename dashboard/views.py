from django.views import generic
from django.http import HttpRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from typing import Any, Dict
import json
from django.utils import timezone


from stores.utils import get_stores_count
from products.utils import get_products_count
from sales.utils import aggregate_sales_count, aggregate_revenue_from_sales
from products.models import ProductCategories



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
        context["product_categories"] = ProductCategories.labels
        return context
    


class DashboardStatisticsView(LoginRequiredMixin, generic.View):
    """View for retrieving dashboard statistics."""
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles dashboard statistics AJAX/Fetch POST request"""
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



dashboard_view = DashboardView.as_view()
dashboard_stats_view = DashboardStatisticsView.as_view()
