from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from sales.models import Sale
from stores.mixins import StoreQuerySetMixin, SupportsQuerySetFiltering
from users.mixins import RequestUserQuerySetMixin
from .utils import get_total_sales_revenue


sale_queryset = Sale.objects.all().select_related("store", "product")


class SalesReportView(
    SupportsQuerySetFiltering,
    RequestUserQuerySetMixin,
    StoreQuerySetMixin,
    LoginRequiredMixin, 
    generic.ListView
):
    """View for generating store sales report."""
    model = Sale
    queryset = sale_queryset
    context_object_name = "sales"
    http_method_names = ["get"]
    template_name = "reports/sales_report.html"

    # For the StoreQuerySetMixin
    store_field = "store"
    store_identifier = "slug"
    store_url_kwarg = "store_slug"

    # For the RequestUserQuerySetMixin
    user_field = "store__owner"

    # For the SupportsQuerySetFiltering mixin
    filter_mappings = {
        "color": "product__color__iexact",
        "size": "product__size",
        "weight": "product__weight",
        "categories": "product__category__in",
        "brands": "product__brand__pk__in",
        "groups": "product__group__pk__in",
        "min_quantity": "quantity__gte",
        "max_quantity": "quantity__lte",
        "min_price": "product__price__gte",
        "max_price": "product__price__lte",
        "date": "made_at__date",
        "from_date": "made_at__date__gte",
        "to_date": "made_at__date__lte",
        "from_time": "made_at__time__gte",
        "to_time": "made_at__time__lte",
    }

    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        sales = context["sales"]
        if sales:
            context["total_revenue"] = get_total_sales_revenue(sales)
            context["total_quantity_sold"] = sum(sale.quantity for sale in sales)

        store = self._get_store()
        context["store"] = store
        context["has_made_sales"] = Sale.objects.filter(store=store).exists()
        return context


sales_report_view = SalesReportView.as_view()
