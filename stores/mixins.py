from django.db.models import QuerySet
from djmoney.money import Money
from decimal import Decimal

from .models import Store
from products.models import ProductCategories



class StoreQuerySetMixin:
    """
    Mixin to get the queryset of the store specified in the URL.

    The following attributes allow customization of the mixin:
    - store_fieldname: The name of the field in the model that stores the store object.
    - store_identifier: The name of the field in the store model that holds a unique identifier.
    - store_url_kwarg: The name of the URL keyword argument that hold the store identifier.
    """
    store_fieldname = "store"
    store_url_kwarg = "store_id"
    store_identifier = "pk"

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        store_identifier_value = self.kwargs.get(self.store_url_kwarg)
        return super().get_queryset(*args, **kwargs).filter(
            **{f"{self.store_fieldname}__{self.store_identifier}": store_identifier_value}
        )



ALLOWED_FILTER_PARAMS = (
    "categories",
    "brands",
    "groups",
    "color",
    "min_quantity",
    "max_quantity",
    "size",
    "weight",
    "min_price",
    "max_price",
    "date",
    "from_date",
    "to_date",
    "from_time",
    "to_time",
)

LIST_TYPE_FILTERS = (
    "categories",
    "brands",
    "groups",
)


class SupportsQuerySetFiltering:
    """
    Mixin to support filtering of a store's queryset by request query parameters.

    The following attributes allow customization of the mixin:

    - filter_mappings - A mapping of the possible filter param names for the view, to its 
    corresponding query filter(that will be used to filter the queryset).
    
    #### For example:
    ```python
    class ProductListView(SupportsQuerySetFiltering, generic.ListView):
        ...
        filter_mappings = {
            ...
            "date": "added_at__date",
            ...
        }
    ```
    So the queryset will be filtered by the `added_at__date` field if the `date` query parameter is present in the request.
    For example, a request to `/products/?date=2021-10-10` will filter the queryset as follows:
    ```python
    qs = queryset.filter(added_at__date="2021-10-10")
    ```

    #### Using the filters card in the views template
    Include the filters card in the views template thus;

    The stylesheet:
    ```html
    <link rel="stylesheet" href="{% static 'base//styles//filters_card.css' %}">
    ```

    The markup:
    ```html
    {% include "base/filters_card.html" %}
    ```

    And the scripts:
    ```html
    <script src="{% static 'base//scripts//filtersCard.js' %}"></script>
    <script src="{% static 'base//scripts//usesFiltersCard.js' %}"></script>
    ```
    """
    filter_mappings = {}

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        self._check_filter_mappings()
        queryset = super().get_queryset(*args, **kwargs)
        filters = self.process_filter_params(self.request.GET.dict())
        if not filters:
            return queryset
        return queryset.filter(**filters)
    

    def _check_filter_mappings(self) -> None:
        invalid = []
        for param in self.filter_mappings:
            if param in ALLOWED_FILTER_PARAMS:
                continue
            invalid.append(param)

        if invalid:
            raise ValueError(f"Invalid filter params, '{", ".join(param)}', in filter_mappings!")
        return None
    

    def _get_store(self) -> Store | None:
        return Store.objects.filter(slug=self.kwargs.get("store_slug")).first()
    

    def process_filter_params(self, params: dict) -> dict:
        """
        Process the request query parameters based on the the `Filter param : Query filter` in `filter_mappings`.
        Returns a dictionary of suitable filters to filter the queryset by

        :param params: The request query parameters that are present as keys in `filter_mappings`
        :return: A dictionary of suitable query filters to filter the queryset by.
        """
        query_filters = {}

        for param_name, query_filter in self.filter_mappings.items():
            param_val = params.get(param_name, None)
            if not param_val:
                continue

            if param_name in LIST_TYPE_FILTERS:
                param_val = param_val.split(",")

            if "price" in param_name:
                store = self._get_store()
                param_val = Money(Decimal(param_val), store.default_currency) if store else Money(Decimal(param_val), "NGN")

            query_filters[query_filter] = param_val
        return query_filters


    def get_context_data(self, *args, **kwargs) -> dict:
        context = super().get_context_data(*args, **kwargs)
        context["filters"] = list(self.filter_mappings.keys())
        context["filter_title"] = f"Filter {self.context_object_name} by"
        context["categories"] = ProductCategories.choices

        store = self._get_store()
        if store:
            context["brands"] = store.product_brands.all()
            context["groups"] = store.product_groups.all()
        return context
