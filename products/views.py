from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views import generic
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import redirect
import json
from decimal import Decimal

from .models import Product, ProductCategories
from stores.models import Store
from stores.mixins import StoreQuerySetMixin
from users.mixins import RequestUserQuerySetMixin
from stores.decorators import store_authorization_required
from users.decorators import requires_password_verification
from .forms import ProductForm
from .utils import _fetch_existing_product_copy, _update_product_data_with_new_brand_and_group

product_queryset = Product.objects.all().select_related("store", "brand", "group")


class ProductListView(
        RequestUserQuerySetMixin, 
        StoreQuerySetMixin, 
        LoginRequiredMixin, 
        generic.ListView
    ):
    """View for listing products in a store."""
    queryset = product_queryset
    context_object_name = "products"
    template_name = "products/product_list.html"
    paginate_by = 40
    # For the StoreQuerySetMixin
    store_fieldname = "store"
    store_identifier = "slug"
    store_url_kwarg = "store_slug"
    # For the RequestUserQuerySetMixin
    user_fieldname = "store__owner"

    def get_store(self) -> Any:
        return Store.objects.get(slug=self.kwargs.get("store_slug"))
    

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["store"] = self.get_store()
        context["product_categories"] = ProductCategories.choices
        return context
    

    @store_authorization_required(identifier="slug", url_kwarg="store_slug")
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)



class ProductAddView(LoginRequiredMixin, generic.CreateView):
    """Handles AJAX/Fetch requests to add a product to a store."""
    model = Product
    form_class = ProductForm
    http_method_names = ["post"]

    @store_authorization_required(identifier="slug", url_kwarg="store_slug")
    def post(self, request, *args, **kwargs) -> JsonResponse:
        store = Store.objects.get(slug=kwargs.get("store_slug"))
        data: Dict = json.loads(request.body)
        data["price_0"] = Decimal(data.pop("price", 0))
        data["price_1"] = store.default_currency
        data["store"] = store.pk

        # Check if product already exists and update its quantity instead
        existing_copy = _fetch_existing_product_copy(data)
        if existing_copy:
            existing_copy.quantity += int(data.get("quantity", 0))
            existing_copy.save()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Product already exists!",
                    "redirect_url": reverse("stores:products:product_list", kwargs={"store_slug": existing_copy.store.slug})
                },
                status=200
            )

        # Update product data with new brand and group
        data, errors = _update_product_data_with_new_brand_and_group(data)

        form = self.get_form_class()(data=data)
        if form.is_valid() and not errors:
            product: Product = form.save(commit=True)
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Product added successfully!",
                    "redirect_url": reverse("stores:products:product_list", kwargs={"store_slug": product.store.slug})
                },
                status=201
            )

        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred while adding product!",
                "errors": {**form.errors, **errors}
            },
            status=400
        )
    


class ProductUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Handles AJAX/Fetch requests to update a product in a store."""
    model = Product
    queryset = product_queryset
    form_class = ProductForm
    http_method_names = ["get", "post"]
    context_object_name = "product"
    pk_url_kwarg = "product_id"
    template_name = "products/product_update.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["product_categories"] = ProductCategories.choices
        return context
    

    @store_authorization_required(identifier="slug", url_kwarg="store_slug")
    def get(self, request, *args, **kwargs) -> HttpResponse:
        return super().get(request, *args, **kwargs)


    @store_authorization_required(identifier="slug", url_kwarg="store_slug")
    def post(self, request, *args, **kwargs) -> JsonResponse:
        data: Dict = json.loads(request.body)
        product: Product = self.get_object()
        data["price_0"] = Decimal(data.pop("price", 0))
        data["price_1"] = product.price.currency
        data["store"] = product.store.pk

        # Update product data with new brand and group
        data, errors = _update_product_data_with_new_brand_and_group(data)

        form = self.get_form_class()(data=data, instance=product)
        if form.is_valid() and not errors:
            product = form.save(commit=True)
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Product updated successfully!",
                    "redirect_url": reverse("stores:products:product_list", kwargs={"store_slug": product.store.slug})
                },
                status=200
            )

        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred while updating product!",
                "errors": {**form.errors, **errors}
            },
            status=400
        )



class ProductDeleteView(LoginRequiredMixin, generic.DetailView):
    """View for deleting a product in a store."""
    model = Product
    queryset = product_queryset
    http_method_names = ["get"]
    pk_url_kwarg = "product_id"

    @store_authorization_required(identifier="slug", url_kwarg="store_slug")
    @requires_password_verification
    def get(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return redirect("stores:products:product_list", store_slug=self.kwargs.get("store_slug"))




product_list_view = ProductListView.as_view()
product_add_view = ProductAddView.as_view()
product_update_view = ProductUpdateView.as_view()
product_delete_view = ProductDeleteView.as_view()
