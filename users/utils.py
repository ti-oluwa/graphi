from typing import List
from django.db import models

from .models import UserAccount
from stores.models import Store


def get_products_count(user: UserAccount) -> int:
    """Get the number of products owned by a user."""
    if not isinstance(user, UserAccount):
        raise TypeError("user must be an instance of UserAccount")

    aggregation = Store.objects.filter(owner=user).aggregate(products_count=models.Count("products"))
    return aggregation["products_count"]


def get_stores_count(user: UserAccount) -> int:
    """Get the number of stores owned by a user."""
    if not isinstance(user, UserAccount):
        raise TypeError("user must be an instance of UserAccount")

    return Store.objects.filter(owner=user).count()


def aggregate_total_sales_by(
        user: UserAccount,
        store_ids: List[str] = None,
        date: str = None,
        from_date: str = None,
        to_date: str = None,
        from_time: str = None,
        to_time: str = None,
    ) -> int:
    if not store_ids:
        store_ids = Store.objects.filter(owner=user).values_list("id", flat=True)

    return sum(
        Store.objects.filter(pk__in=store_ids).values_list("sales", flat=True).annotate(
            total_sales=models.Sum("sales")
        ).values_list("total_sales", flat=True)
    )


def aggregate_total_sales_for_store_by(
        user: UserAccount,
        store_id: str,
        date: str = None,
        from_date: str = None,
        to_date: str = None,
        from_time: str = None,
        to_time: str = None,
    ) -> int:
    ...
