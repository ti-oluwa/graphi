from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.http import HttpRequest, HttpResponse, JsonResponse
from typing import Any, Dict
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import redirect
import json

from .models import Sale
from .forms import SaleForm
from stores.models import Store
from stores.mixins import StoreQuerySetMixin
from stores.decorators import requires_store_authorization, to_JsonResponse
from users.decorators import requires_account_verification, requires_password_verification
from users.mixins import RequestUserQuerySetMixin


sale_queryset = Sale.objects.all().select_related("store", "product")


class SaleListView(
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
    # For the StoreQuerySetMixin
    store_fieldname = "store"
    store_identifier = "slug"
    store_url_kwarg = "store_slug"
    # For the RequestUserQuerySetMixin
    user_fieldname = "store__owner"

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
            
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Sale recorded successfully!",
                    "redirect_url": reverse("stores:sales:sale_list", kwargs={"store_slug": sale.store.slug})
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



class SaleUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Handles AJAX/Fetch requests to update a sale record in a store."""
    model = Sale
    queryset = sale_queryset
    form_class = SaleForm
    http_method_names = ["get", "post"]
    pk_url_kwarg = "sale_id"
    template_name = "sales/sale_update.html"

    @requires_password_verification
    def get(self, request, *args, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)


    @to_JsonResponse
    @requires_account_verification
    def post(self, request, *args, **kwargs) -> JsonResponse:
        data: Dict = json.loads(request.body)
        passkey = data.pop("passkey", None)
        data["owner"] = request.user.pk
        store: Store = self.get_object()

        form = self.get_form_class()(data=data, instance=store)
        if form.is_valid():
            sale = form.save(commit=True)
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Store updated successfully!",
                    "redirect_url": reverse("stores:store_list")
                },
                status=200
            )
            
        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred while updating store!",
                "errors": form.errors,
            },
            status=400
        )



class SaleDeleteView(LoginRequiredMixin, generic.DetailView):
    """View for deleting a sale record from a store."""
    model = Sale
    queryset = sale_queryset
    http_method_names = ["get"]
    pk_url_kwarg = "sale_id"

    @requires_password_verification
    def get(self, request, *args, **kwargs):
        sale = self.get_object()
        sale.delete()
        return redirect("stores:sales:sale_list", store_slug=self.kwargs.get("store_slug"))




sale_list_view = SaleListView.as_view()
sale_add_view = SaleAddView.as_view()
sale_update_view = SaleUpdateView.as_view()
sale_delete_view = SaleDeleteView.as_view()
