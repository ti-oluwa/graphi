import json
import re
from typing import Any
from django.db.models.query import QuerySet
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect
from djmoney.settings import CURRENCY_CHOICES


from .models import Store, StoreTypes
from .forms import StoreForm
from .decorators import store_authorization_required, to_JsonResponse


stores_global_queryset = Store.objects.all().prefetch_related("products").select_related("owner")


class StoreAuthorizationView(LoginRequiredMixin, generic.TemplateView):
    http_method_names = ["get", "post"]
    template_name = 'stores/store_auth.html'

    def get(self, request, *args, **kwargs) -> HttpResponse:
        store_id  = request.GET.get('store_id')
        if not store_id:
            return HttpResponse(
                status=400, 
                content="Store primary key not provided! Expected a query parameter named 'store_id' but none was found."
            )
        store = get_object_or_404(Store, pk=store_id)
        # Check if request is already authorized
        if store.check_request_is_authorized(request):
            # Redirect to next view if request is already authorized
            return redirect(request.GET.get("next", "/"))
        return super().get(request, *args, **kwargs)
    

    @to_JsonResponse
    def post(self, request, *args, **kwargs) -> JsonResponse:
        store_id_query_param_pattern = r"store_id=(?P<store_id>[a-zA-Z0-9-]+)"
        next_view_query_param_pattern = r"next=(?P<next>[a-zA-Z0-9-\\/]+)"
        request_path = request.META.get("HTTP_REFERER", "")
        store_id_result = re.search(store_id_query_param_pattern, request_path)
        next_view_result = re.search(next_view_query_param_pattern, request_path)

        if not (store_id_result and next_view_result):
            return HttpResponse(
                content="Invalid Request URL!",
                status=400
            )
        
        data = json.loads(request.body)
        store_pk = store_id_result.group("store_id")
        next_url = next_view_result.group("next")
        store_passkey = data.get("passkey", None)
        store = get_object_or_404(Store, pk=store_pk)

        if not store.authorize_request(request, store_passkey):
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Invalid Passkey"
                },
                status=401
            )
        return JsonResponse(
            data={
                "status": "success",
                "detail": "Authorization successful!",
                "redirect_url": next_url
            },
            status=200
        )



class AddStoreTypesAndCurrencyChoicesToContextMixin:
    """Update context with store types and currency choices"""
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["store_types"] = StoreTypes.choices
        context["currencies"] = CURRENCY_CHOICES
        return context



class StoreListView(
        AddStoreTypesAndCurrencyChoicesToContextMixin,
        LoginRequiredMixin, 
        generic.ListView
    ):
    model = Store
    template_name = "stores/store_list.html"
    context_object_name = "stores"
    queryset = stores_global_queryset
    paginate_by = 4
    form_class = StoreForm

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(owner=self.request.user)
    
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["types_count"] = self.get_queryset().values("type").distinct().count()
        return context



class StoreCreateView(LoginRequiredMixin, generic.CreateView):
    model = Store
    form_class = StoreForm
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs) -> JsonResponse:
        data = json.loads(request.body)
        passkey = data.pop("passkey", None)
        form = self.get_form_class()(data=data)

        if form.is_valid():
            store: Store = form.save(commit=False)
            store.owner = request.user
            if passkey:
                try:
                    store.set_passkey(passkey)
                except (TypeError, ValueError) as exc:
                    return JsonResponse(
                        data={
                            "status": "error",
                            "detail": str(exc),
                        },
                        status=400
                    )
            
            store.save()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Store created successfully!",
                    "redirect_url": reverse("stores:store_list")
                },
                status=201
            )
            
        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred while creating store!",
                "errors": form.errors,
            },
            status=400
        )



class StoreUpdateView(
        AddStoreTypesAndCurrencyChoicesToContextMixin,
        LoginRequiredMixin, 
        generic.UpdateView
    ):
    model = Store
    form_class = StoreForm
    http_method_names = ["get", "post"]
    pk_url_kwarg = "store_id"
    template_name = "stores/store_update.html"

    @store_authorization_required("store_id")
    def get(self, request, *args, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)


    def post(self, request, *args, **kwargs) -> JsonResponse:
        data = json.loads(request.body)
        passkey = data.pop("passkey", None)
        store: Store = self.get_object()
        form = self.get_form_class()(data=data, instance=store)
        if form.is_valid():
            store = form.save(commit=False)
            if passkey:
                try:
                    store.set_passkey(passkey)
                except (TypeError, ValueError) as exc:
                    return JsonResponse(
                        data={
                            "status": "error",
                            "detail": str(exc),
                        },
                        status=400
                    )
            store.save()

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



class StoreDeleteView(
        AddStoreTypesAndCurrencyChoicesToContextMixin,
        LoginRequiredMixin, 
        generic.DetailView
    ):
    model = Store
    http_method_names = ["get"]
    pk_url_kwarg = "store_id"

    @store_authorization_required("store_id")
    def get(self, request, *args, **kwargs):
        store = self.get_object()
        store.delete()
        return redirect("stores:store_list")



store_auth_view = StoreAuthorizationView.as_view()
store_list_view = StoreListView.as_view()
store_create_view = StoreCreateView.as_view()
store_update_view = StoreUpdateView.as_view()
store_delete_view = StoreDeleteView.as_view()
