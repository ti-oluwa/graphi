from typing import List

from users.models import UserAccount
from stores.models import Store


def get_stores_count(user: UserAccount) -> int:
    """Returns the number of stores owned by a user."""
    if not isinstance(user, UserAccount):
        raise TypeError("user must be an instance of UserAccount")

    return Store.objects.filter(owner=user).count()


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

