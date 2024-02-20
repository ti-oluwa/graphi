from django.db.models import QuerySet

from .managers import SearchableQuerySet


class RequestUserQuerySetMixin:
    """
    Mixin to get only the queryset of the user making the request.

    The following attributes allow customization of the mixin:
    - user_field: The name of the field in the model that stores the user object. Can be a complex lookup.
    E.g. "store__owner" to get the owner of the store.
    """
    user_field = "user"

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        return super().get_queryset(*args, **kwargs).filter(
            **{self.user_field: self.request.user}
        )



class QuerySetSearchMixin:
    """
    Mixin to add search functionality to a view. The view's queryset must be a `SearchableQuerySet`,
    i.e `get_queryset` must return a `SearchableQuerySet`.

    The following attributes allow customization of the mixin:
    - search_fields: The fields to search in the view model/queryset.
    - url_search_param: The name of the URL parameter that contains the search query. Default is "query".
    """

    search_fields = []
    url_search_param = "query"

    def get_queryset(self, *args, **kwargs) -> SearchableQuerySet:
        qs = super().get_queryset(*args, **kwargs)
        if not isinstance(qs, SearchableQuerySet):
            raise TypeError(
                "View model or queryset does not support search."
                f"`get_queryset` must return a `{SearchableQuerySet.__name__}`. Got {qs.__class__.__name__} instead."
            )
        
        query = self.request.GET.get(self.url_search_param, "")
        if not query:
            return qs
        return qs.search(query, self.search_fields)
