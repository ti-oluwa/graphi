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
        store_pk_url_kwarg: str,
        auth_view: str = settings.STORE_AUTHORIZATION_VIEW,
    ):
    """
    Returns a decorator that ensures that a request to a view is authorized to access a store.

    :param store_pk_url_kwarg: The name of the URL keyword argument that contains the store's primary key.
    :param auth_view: The name of the view to redirect to if the request is not authorized. Defaults to the value of the
        STORE_AUTHORIZATION_VIEW setting.
    """
    def decorator(func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        """
        Ensures that a request to a view is authorized to access a store.
        """
        @functools.wraps(func)
        def wrapper(view: View, request: HttpRequest, *args, **kwargs) -> HttpResponse | HttpResponseRedirect:
            if not auth_view:
                return ValueError(
                    "No authorization view provided! Provide a value for the 'auth_view' argument or set the STORE_AUTHORIZATION_VIEW setting."
                )
            
            store_pk = kwargs.get(store_pk_url_kwarg)
            if not store_pk:
                return HttpResponse(
                    status=400, 
                    content=f"Store primary key not provided! Expected a keyword argument named \
                        '{store_pk_url_kwarg or view.pk_url_kwarg}' but none was found."
                )
            
            store = get_object_or_404(Store, pk=store_pk)
            if not store.check_request_is_authorized(request):
                auth_url = reverse(auth_view)
                redirect_url = f"{auth_url}?store_id={store.pk}&next={request.path}"
                return redirect(redirect_url, permanent=False)

            return func(view, request, *args, **kwargs)
        return wrapper
    
    return decorator

