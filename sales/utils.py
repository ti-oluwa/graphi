from typing import Any, List, Dict
from djmoney.money import Money
import uuid
from decimal import Decimal

from users.models import UserAccount
from .models import Sale
from stores.utils import filter_store_pks_for_user


def get_aggregation_filters(
        store_pks: List[str | uuid.UUID] = None,
        categories: List[str] = None,
        date: str = None,
        from_date: str = None,
        to_date: str = None,
        from_time: str = None,
        to_time: str = None,
    ) -> Dict[str, Any]:
    """
    Returns a dictionary of filters to be used to aggregate sales based on the given parameters.

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
        filters["product__category__in"] = [ category.lower() for category in categories ]
    return filters



def aggregate_revenue_from_sales(
        user: UserAccount,
        store_pks: List[str | uuid.UUID] = None,
        categories: List[str] = None,
        date: str = None,
        from_date: str = None,
        to_date: str = None,
        from_time: str = None,
        to_time: str = None,
        max_decimal_places: int = 2,
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
    :param max_decimal_places: The maximum number of decimal places to round the revenue to.
    :return: The aggregated total revenue made from sales.
    """
    store_pks = filter_store_pks_for_user(user, store_pks)
    sales_filters = get_aggregation_filters(store_pks, categories, date, from_date, to_date, from_time, to_time)
    sales_filters["store__owner"] = user
    # If no aggregation filter, return 0 revenue
    if not sales_filters:
        return Money(Decimal(0), user.preferred_currency).round(max_decimal_places)
    return Sale.get_total_revenue(currency=user.preferred_currency, **sales_filters).round(max_decimal_places)



def aggregate_sales_count(
        user: UserAccount,
        store_pks: List[str | uuid.UUID] = None,
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
    sales_filters = get_aggregation_filters(store_pks, categories, date, from_date, to_date, from_time, to_time)
    sales_filters["store__owner"] = user
    
    if not sales_filters:
        return 0
    return Sale.get_count(**sales_filters)

