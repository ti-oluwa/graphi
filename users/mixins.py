from django.db.models import QuerySet


class RequestUserQuerySetMixin:
    """
    Mixin to get only the queryset of the user making the request.

    The following attributes allow customization of the mixin:
    - user_fieldname: The name of the field in the model that stores the user object. Can be a complex lookup.
    E.g. "store__owner" to get the owner of the store.
    """
    user_fieldname = "user"

    def get_queryset(self, *args, **kwargs) -> QuerySet:
        return super().get_queryset(*args, **kwargs).filter(
            **{self.user_fieldname: self.request.user}
        )
