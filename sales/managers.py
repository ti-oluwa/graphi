from __future__ import annotations
from typing import Any

from users.managers import SearchableModelManager, SearchableQuerySet


class SaleQuerySet(SearchableQuerySet):

    def search(self, query: str | Any, fields: list[str] | str = None) -> SaleQuerySet:
        if not fields:
            fields = [
                "product__name", "product__category", "store__name", "store__type",
                "payment_method"
            ]
        return super().search(query, fields)


class SaleManager(SearchableModelManager.from_queryset(SaleQuerySet)):
    '''Custom manager for the `Sale` model.'''

    
