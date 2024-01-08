from typing import Any, Callable
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect


def redirect_authenticated(redirect_view: Callable | str):
    """
    Create a decorator that redirects authenticated users to a view.

    :param redirect_view: The view to redirect to. Could be a view, view name or url.
    """
    def decorator(view_func: Callable[..., HttpResponse | JsonResponse]):
        """
        Decorator that redirects authenticated users to a view.

        :param view_func: The view function to decorate.
        """
        def wrapper(self, request: HttpRequest, *args: str, **kwargs: Any):
            if request.user.is_authenticated:
                return redirect(redirect_view)
            return view_func(self, request, *args, **kwargs)
        return wrapper
    
    return decorator
