from math import e
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import HttpRequest, HttpResponse, JsonResponse
from typing import Any, Dict
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import redirect
import json
from urllib.parse import urlencode as urllib_urlencode

from .models import Sale
from .forms import SaleForm
from stores.models import Store
from stores.mixins import StoreQuerySetMixin, SupportsQuerySetFiltering
from stores.decorators import requires_store_authorization, to_JsonResponse
from users.decorators import requires_account_verification, requires_password_verification
from users.mixins import RequestUserQuerySetMixin
from users.utils import parse_query_params_from_request


sale_queryset = Sale.objects.all().select_related("store", "product")


class SaleListView(
    SupportsQuerySetFiltering,
    RequestUserQuerySetMixin,
    StoreQuerySetMixin,
    LoginRequiredMixin, 
    generic.ListView
):
    """View for listing sales in a store."""
    model = Sale
    queryset = sale_queryset
    context_object_name = "sales"
    template_name = "sales/sale_list.html"
    http_method_names = ["get"]
    paginate_by = 20

    # For the StoreQuerySetMixin
    store_fieldname = "store"
    store_identifier = "slug"
    store_url_kwarg = "store_slug"

    # For the RequestUserQuerySetMixin
    user_fieldname = "store__owner"

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
        "date": "made_at__date",
        "from_date": "made_at__date__gte",
        "to_date": "made_at__date__lte",
        "from_time": "made_at__time__gte",
        "to_time": "made_at__time__lte",
    }

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["todays_sales"] = self.get_queryset().filter(
            made_at__date=user.to_local_timezone(timezone.now()).date()
        )
        context["store"] = Store.objects.get(slug=self.kwargs["store_slug"])
        return context


    @requires_store_authorization(identifier="slug", url_kwarg="store_slug")
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)



class SaleAddView(LoginRequiredMixin, generic.CreateView):
    """View for adding a new sale record to a store."""
    model = Sale
    form_class = SaleForm
    http_method_names = ["post"]

    @requires_store_authorization(identifier="slug", url_kwarg="store_slug")
    @to_JsonResponse
    @requires_account_verification
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        store = Store.objects.get(slug=kwargs.get("store_slug"))
        data: Dict = json.loads(request.body)
        data["store"] = store.pk

        form = self.get_form_class()(data=data)
        if form.is_valid():
            try:
                sale: Sale = form.save(commit=True)
            except Exception as exc:
                return JsonResponse(
                    data={
                        "status": "error",
                        "detail": exc.args[0] if exc.args else str(exc)
                    },
                    status=400
                )
            
            sale_list_url = reverse("stores:sales:sale_list", kwargs={"store_slug": sale.store.slug})
            redirect_url = f'{sale_list_url}?date={sale.made_at_utz.date()}'
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Sale recorded successfully!",
                    "redirect_url": redirect_url
                },
                status=201
            )

        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred while recording the sale!",
                "errors": form.errors
            },
            status=400
        )



class SaleUpdateView(StoreQuerySetMixin, LoginRequiredMixin, generic.UpdateView):
    """Handles AJAX/Fetch requests to update a sale record in a store."""
    model = Sale
    queryset = sale_queryset
    form_class = SaleForm
    http_method_names = ["get", "post"]
    pk_url_kwarg = "sale_id"
    template_name = "sales/sale_update.html"
    context_object_name = "sale"

    # For the StoreQuerySetMixin
    store_fieldname = "store"
    store_identifier = "slug"
    store_url_kwarg = "store_slug"

    @requires_store_authorization(identifier="slug", url_kwarg="store_slug")
    def get(self, request, *args, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)


    @to_JsonResponse
    @requires_account_verification
    def post(self, request, *args, **kwargs) -> JsonResponse:
        data: Dict = json.loads(request.body)
        sale: Sale = self.get_object()
        data["store"] = sale.store.pk

        form = self.get_form_class()(data=data, instance=sale)
        if form.is_valid():
            try:
                sale: Sale = form.save(commit=True)
            except Exception as exc:
                return JsonResponse(
                    data={
                        "status": "error",
                        "detail": exc.args[0] if exc.args else str(exc)
                    },
                    status=400
                )
            
            sale_list_url = reverse("stores:sales:sale_list", kwargs={"store_slug": sale.store.slug})
            redirect_url = f'{sale_list_url}?date={sale.made_at_utz.date()}'
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Sale updated successfully!",
                    "redirect_url": redirect_url
                },
                status=200
            )
            
        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred while updating sale!",
                "errors": form.errors,
            },
            status=400
        )



class SaleDeleteView(StoreQuerySetMixin, LoginRequiredMixin, generic.DetailView):
    """View for deleting a sale record from a store."""
    model = Sale
    queryset = sale_queryset
    http_method_names = ["get"]
    pk_url_kwarg = "sale_id"

    # For the StoreQuerySetMixin
    store_fieldname = "store"
    store_identifier = "slug"
    store_url_kwarg = "store_slug"

    @requires_password_verification
    def get(self, request, *args, **kwargs):
        sale = self.get_object()
        sale_list_url = reverse("stores:sales:sale_list", kwargs={"store_slug": sale.store.slug})
        redirect_url = f'{sale_list_url}?date={sale.made_at_utz.date()}'
        sale.delete()
        return redirect(redirect_url)




sale_list_view = SaleListView.as_view()
sale_add_view = SaleAddView.as_view()
sale_update_view = SaleUpdateView.as_view()
sale_delete_view = SaleDeleteView.as_view()
