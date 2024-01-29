from typing import Callable
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
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


def store_authorization_required(
        view_func: Callable = None, 
        *, 
        identifier: str = "pk",
        url_kwarg: str = "store_id",
        auth_view: str = settings.STORE_AUTHORIZATION_VIEW,
    ):
    """
    Decorator that ensures that a request is authorized to access a store.

    :param identifier: The key to be used to retrieve the store in the db query. Defaults to 'pk'.
    :param url_kwarg: The name of the URL keyword argument that contains the value of the store's identifier. Defaults to 'store_id'.
    :param auth_view: The name of the view to redirect to if the request is not authorized. Defaults to the value of the
        STORE_AUTHORIZATION_VIEW setting.
    """
    def decorator(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        """
        Ensures that a request to a view is authorized to access a store.
        """
        @functools.wraps(view_func)
        def wrapper(view: View, request: HttpRequest, *args, **kwargs) -> HttpResponse | HttpResponseRedirect:
            if not auth_view:
                return ValueError(
                    "No authorization view provided! Provide a value for the 'auth_view' argument or set the STORE_AUTHORIZATION_VIEW setting."
                )
            
            identifier_value = kwargs.get(url_kwarg)
            if not identifier_value:
                return HttpResponse(
                    status=400, 
                    content=f"Store identifier '{url_kwarg}' not found! Expected a URL keyword argument named '{url_kwarg}' but none was found."
                )
            
            store = get_object_or_404(Store, **{identifier: identifier_value})
            if not store.check_request_is_authorized(request):
                auth_url = reverse(auth_view)
                redirect_url = f"{auth_url}?{identifier}={identifier_value}&next={request.path}"
                return redirect(redirect_url, permanent=False)

            return view_func(view, request, *args, **kwargs)
        return wrapper
    
    if view_func:
        return decorator(view_func)
    return decorator

