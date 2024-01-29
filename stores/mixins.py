

class StoreQuerySetMixin:
    """
    Mixin to get the queryset of the store specified in the URL.

    The following attributes allow customization of the mixin:
    - store_fieldname: The name of the field in the model that stores the store object.
    - store_identifier: The name of the field in the store model that holds a unique identifier.
    - store_url_kwarg: The name of the URL keyword argument that hold the store identifier.
    """
    store_fieldname = "store"
    store_url_kwarg = "store_id"
    store_identifier = "pk"

    def get_queryset(self, *args, **kwargs):
        store_identifier_value = self.kwargs.get(self.store_url_kwarg)
        return super().get_queryset(*args, **kwargs).filter(
            **{f"{self.store_fieldname}__{self.store_identifier}": store_identifier_value}
        )
