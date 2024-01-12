from typing import List
from django.db import models
from djmoney.money import Money
from django.utils import timezone

from .models import UserAccount
from stores.models import Store
from sales.models import Sale


def get_products_count(user: UserAccount) -> int:
    """Returns the number of products added by a user."""
    if not isinstance(user, UserAccount):
        raise TypeError("user must be an instance of UserAccount")

    aggregation = Store.objects.filter(owner=user).aggregate(products_count=models.Count("products"))
    return aggregation["products_count"]



def get_stores_count(user: UserAccount) -> int:
    """Returns the number of stores owned by a user."""
    if not isinstance(user, UserAccount):
        raise TypeError("user must be an instance of UserAccount")

    return Store.objects.filter(owner=user).count()



def _process_aggregation_filters(
        store_pks: List[str] = None,
        categories: List[str] = None,
        date: str = None,
        from_date: str = None,
        to_date: str = None,
        from_time: str = None,
        to_time: str = None,
    ) -> dict:
    """
    Processes the given aggregation filters and returns a dictionary of filters
    that can be used to filter sales.

    :param store_pks: A list of primary keys of the stores whose sales will be used during aggregation.
    If not provided, all the stores owned by the user will be used.
    :param date: If provided, only sales made on the given date will be used during aggregation.
    If provided, `from_date` and `to_date` will be ignored.
    :param from_date: If provided, only sales made on or after the given date will be used during aggregation.
    :param to_date: If provided, only sales made on or before the given date will be used during aggregation.
    :param from_time: If provided, only sales made on or after the given time will be used during aggregation.
    :param to_time: If provided, only sales made on or before the given time will be used during aggregation.
    :return: A dictionary of filters that can be used to filter sales.
    """
    filters = {}
    if date:
        filters["made_at__date"] = date
    else:
        if from_date:
            filters["made_at__date__gte"] = from_date
        if to_date:
            filters["made_at__date__lte"] = to_date
    if from_time:
        filters["made_at__time__gte"] = from_time
    if to_time:
        filters["made_at__time__lte"] = to_time

    if store_pks:
        filters["store__pk__in"] = store_pks

    if categories:
        filters["product__category__in"] = [category.lower() for category in categories]

    return filters



def filter_store_pks_for_user(user: UserAccount, store_pks: List[str] = None) -> List[str]:
    """
    Filters the given store primary keys to only include the primary keys of the stores
    owned by the given user.

    :param user: The user with which the primary keys of stores will be filtered by.
    :param store_pks: A list of primary keys of the stores to be filtered.
    If not provided, all the stores owned by the user will be used.
    :return: A list of primary keys of the stores owned by the user.
    """
    if not isinstance(user, UserAccount):
        raise TypeError("user must be an instance of UserAccount")
    if not store_pks:
        return Store.objects.filter(owner=user).values_list("pk", flat=True)
    return Store.objects.filter(owner=user, pk__in=store_pks).values_list("pk", flat=True)



def aggregate_revenue_from_sales(
        user: UserAccount,
        store_pks: List[str] = None,
        categories: List[str] = None,
        date: str = None,
        from_date: str = None,
        to_date: str = None,
        from_time: str = None,
        to_time: str = None,
    ) -> Money:
    """
    Calculates and returns the total revenue made from sales by a user
    based on the given parameters.

    :param user: The user whose sales revenue is to be aggregated.
    :param store_pks: A list of primary keys of the stores whose sales will be used during aggregation.
    If not provided, all the stores owned by the user will be used.
    :param categories: A list of product categories whose sales will be used during aggregation.
    :param date: If provided, only sales made on the given date will be used during aggregation.
    If provided, `from_date` and `to_date` will be ignored.
    :param from_date: If provided, only sales made on or after the given date will be used during aggregation.
    :param to_date: If provided, only sales made on or before the given date will be used during aggregation.
    :param from_time: If provided, only sales made on or after the given time will be used during aggregation.
    :param to_time: If provided, only sales made on or before the given time will be used during aggregation.
    :return: The aggregated total revenue made from sales.
    """
    store_pks = filter_store_pks_for_user(user, store_pks)
    sales_filters = _process_aggregation_filters(store_pks, categories, date, from_date, to_date, from_time, to_time)
    return Sale.get_total_revenue(currency=user.preferred_currency, **sales_filters)



def aggregate_sales_count(
        user: UserAccount,
        store_pks: List[str] = None,
        categories: List[str] = None,
        date: str = None,
        from_date: str = None,
        to_date: str = None,
        from_time: str = None,
        to_time: str = None,
    ) -> int:
    """
    Calculates and returns the total number of sales made by a user
    based on the given parameters.

    :param user: The user whose sales count is to be aggregated.
    :param store_pks: A list of primary keys of the stores whose sales will be used during aggregation.
    :param categories: A list of product categories whose sales will be used during aggregation.
    If not provided, all the stores owned by the user will be used.
    :param date: If provided, only sales made on the given date will be used during aggregation.
    If provided, `from_date` and `to_date` will be ignored.
    :param from_date: If provided, only sales made on or after the given date will be used during aggregation.
    :param to_date: If provided, only sales made on or before the given date will be used during aggregation.
    :param from_time: If provided, only sales made on or after the given time will be used during aggregation.
    :param to_time: If provided, only sales made on or before the given time will be used during aggregation.
    :return: The aggregated total number of sales made.
    """
    store_pks = filter_store_pks_for_user(user, store_pks)
    sales_filters = _process_aggregation_filters(store_pks, categories, date, from_date, to_date, from_time, to_time)
    return Sale.get_count(**sales_filters)
