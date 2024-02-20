from __future__ import annotations
from typing import Any

from users.managers import SearchableModelManager, SearchableQuerySet


class ProductQuerySet(SearchableQuerySet):

    def search(self, query: str | Any, fields: list[str] | str = None) -> ProductQuerySet:
        if not fields:
            fields = [
                "name", "category", "color", "size", "weight",
                "group__name", "brand__name"
            ]
        return super().search(query, fields)
    

class ProductManager(SearchableModelManager.from_queryset(ProductQuerySet)):
    '''Custom manager for the `Product` model.'''

