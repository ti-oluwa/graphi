from django.db import models
from typing import Any, Dict

from products.models import Product
from stores.models import Store



def get_most_sold_product(product_qs: models.QuerySet[Product], sales_filters: Dict[str, Any] = None) -> Product | None:
    """
    Returns the most sold product in the given queryset of products.

    :param product_qs: A queryset of products to be searched for the most sold product.
    :param sales_filters: A dictionary of filters on which each product's sales will be filtered by.
    """
    if sales_filters:
        filters = {f'sales__{key}': value for key, value in sales_filters.items()}
        get_sales_count = models.Count("sales", filter=models.Q(**filters))
    else:
        get_sales_count = models.Count("sales")
    return product_qs.annotate(sales_count=get_sales_count).order_by("-sales_count").first()



def get_most_active_store(store_qs: models.QuerySet[Store], sales_filters: Dict[str, Any] = None) -> Store | None:
    """
    Returns the store with the most amount of sales made in the given queryset of products.

    :param product_qs: A queryset of stores to be searched for the most active.
    :param sales_filters: A dictionary of filters on which each store's sales will be filtered by.
    """
    if sales_filters:
        filters = {f'sales__{key}': value for key, value in sales_filters.items()}
        get_sales_count = models.Count("sales", filter=models.Q(**filters))
    else:
        get_sales_count = models.Count("sales")
    return store_qs.annotate(sales_count=get_sales_count).order_by("-sales_count").first()
