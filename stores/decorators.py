from typing import Callable
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import View
import json
import functools

from .models import Store


def to_JsonResponse(func: Callable[..., HttpResponse]) -> Callable[..., JsonResponse]:
    """Ensures that the decorated view returns a JsonResponse."""
    @functools.wraps(func)
    def wrapper(request: HttpRequest, *args, **kwargs) -> JsonResponse:
        response = func(request, *args, **kwargs)
        if isinstance(response, HttpResponse):
            return JsonResponse(
                data={
                    "status": "error" if response.status_code >= 400 else "success",
                    "detail": response.content.decode(),
                }, 
                status=response.status_code
            )
        return response
    
    return wrapper


def passkey_authorization_required(
        passkey_field: str = "passkey",
        store_pk_field: str = "store_id",
        message: str = "Unauthorized access to store!",
        view_response_type: str = "http"
    ):
    """
    Returns a decorator that authorizes a request to access a store using a passkey.

    :param passkey_field: The name of the field in the request body that contains the passkey.
    :param store_pk_field: The name of the keyword argument in the view function that contains the store's primary key.
    :param message: The message to return if the request is not authorized.
    :param view_response_type: The type of response the view returns. Can be "http" or "json".
    """
    def decorator(func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse] | Callable[..., JsonResponse]:
        """
        Authorizes a request to decoratored view for access to a store using a passkey.
        """
        @functools.wraps(func)
        def wrapper(view: View, request: HttpRequest, *args, **kwargs) -> HttpResponse | JsonResponse:
            passkey = json.loads(request.body).pop(passkey_field, None)
            store_id = kwargs.get(store_pk_field)
            if not passkey or not store_id:
                return HttpResponse(status=400)

            store = Store.objects.get(pk=store_id)
            if not store.check_request_is_authorized(request) and not store.authorize_request(request, passkey):
                return HttpResponse(status=401, content=message)

            return func(view, request, *args, **kwargs)
        
        if view_response_type == "json":
            return to_JsonResponse(wrapper)
        return wrapper
    
    return decorator

