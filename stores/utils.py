from typing import List, Tuple
import uuid
import datetime
from django.utils import timezone
import inflection

from users.models import UserAccount
from stores.models import Store



def get_stores_count(user: UserAccount) -> int:
    """Returns the number of stores owned by a user."""
    if not isinstance(user, UserAccount):
        raise TypeError("user must be an instance of UserAccount")

    return Store.objects.filter(owner=user).count()


def filter_store_pks_for_user(user: UserAccount, store_pks: List[str | uuid.UUID] = None) -> List[uuid.UUID]:
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
        return list(Store.objects.filter(owner=user).values_list("pk", flat=True))
    return list(Store.objects.filter(owner=user, pk__in=store_pks).values_list("pk", flat=True))


def parse_timeframe_statement(statement: str) -> Tuple[datetime.datetime, datetime.datetime]:
    """
    Converts a timeframe statement into a tuple of datetime objects representing the start and end of the timeframe.

    The statement must be in the format: '<prefix> <number> <time>' e.g 'Past 2 days', 'In 3 hours', 'Next year'
    Allowed prefixes are: 'Past', 'In', 'Next', 'Last'

    :param statement: A string representing a timeframe statement e.g 'Past 2 days', 'In 3 hours', 'Next year'
    :return: A tuple of datetime objects representing the start and end of the timeframe.

    Example:
    >>> parse_timeframe_statement("Past 2 days")
    (
        datetime.datetime(2022, 9, 14, 15, 22, 46, 606000, tzinfo=<UTC>), 
        datetime.datetime(2022, 9, 16, 15, 22, 46, 606000, tzinfo=<UTC>)
    )

    Note: The start and end of the timeframe are timezone aware datetime objects in the server's timezone.
    Convert to the desired timezone using the `astimezone` method.
    """
    allowed_prefixes = ("last", "past", "in", "next")
    negative_delta_prefixes = ("last", "past")
    if not isinstance(statement, str):
        raise TypeError("statement must be a string")
    
    statement = statement.strip()
    if not statement:
        raise ValueError("Empty statement")
    
    parts = statement.split(" ")
    prefix = parts[0].lower()

    if prefix not in allowed_prefixes:
        raise ValueError(
            f"Invalid statement prefix: '{prefix.title()}'. Statement must start with 'Past', 'In' or 'Next' e.g 'Past 2 days' or 'In 3 hours' or 'Next year'"
        )
    
    if len(parts) < 3:
        if len(parts) == 2 and isinstance(parts[1], str):
            parts.insert(1, "1")
        else:
            raise ValueError(
                f"Invalid statement. '{prefix.title()}' statement must take form: '{prefix.title()} <number> <time>' e.g '{prefix.title()} 2 days'"
            )
    
    try:
        duration = float(parts[1])
    except ValueError:
        raise ValueError(
            f"Invalid duration in statement: '{parts[1]}'. Statement must take form: '{prefix.title()} <number> <time>' e.g '{prefix.title()} 2 days'"
        )
    
    if duration < 1.0:
        raise ValueError(f"Duration in statement must be greater than 0")
    try:
        key = inflection.pluralize(parts[2].lower())
        if key == "years":
            key = "weeks"
            duration *= 52
        elif key == "months":
            key = "weeks"
            duration *= 4

        time_delta = timezone.timedelta(**{key: duration})
    except TypeError:
        raise ValueError(f"Unrecognized time statement: '{parts[2]}' in '{statement}'")
    
    now = timezone.now()
    if prefix in negative_delta_prefixes:
        return now - time_delta, now
    return now, now + time_delta
    
