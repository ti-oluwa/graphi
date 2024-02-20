from __future__ import annotations
from typing import Any

from users.managers import SearchableModelManager, SearchableQuerySet


class StoreQuerySet(SearchableQuerySet):

    def search(self, query: str | Any, fields: list[str] | str = None) -> StoreQuerySet:
        if not fields:
            fields = ["name", "type", "email"]
        return super().search(query, fields)


class StoreManager(SearchableModelManager.from_queryset(StoreQuerySet)):
    '''Custom manager for the `Store` model.'''

