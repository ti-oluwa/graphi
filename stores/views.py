from email import message
import json
from typing import Any
from django.db.models.query import QuerySet
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse
from djmoney.settings import CURRENCY_CHOICES


from .models import Store, StoreTypes
from .forms import StoreForm
from .decorators import passkey_authorization_required


stores_global_queryset = Store.objects.all().prefetch_related("products").select_related("owner")


class StoreListView(LoginRequiredMixin, generic.ListView):
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
        context["store_types"] = StoreTypes.choices
        context["currencies"] = CURRENCY_CHOICES
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



class StoreUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Store
    form_class = StoreForm
    http_method_names = ["post"]
    pk_url_kwarg = "store_id"

    @passkey_authorization_required(
        message="Unauthorized to update this store! Provide a valid store passkey.", 
        view_response_type="json"
    )
    def post(self, request, *args, **kwargs) -> JsonResponse:
        data = json.loads(request.body)
        store = self.get_object()
        form = self.get_form_class()(data=data, instance=store)
        if form.is_valid():
            store = form.save(commit=True)
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


store_list_view = StoreListView.as_view()
store_create_view = StoreCreateView.as_view()
store_update_view = StoreUpdateView.as_view()
