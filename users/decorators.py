from typing import Any, Callable
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
import functools
from django.utils import timezone
from django.conf import settings
from dateutil import parser as dateutil_parser


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
        @functools.wraps(view_func)
        def wrapper(self, request: HttpRequest, *args: str, **kwargs: Any):
            if request.user.is_authenticated:
                return redirect(redirect_view)
            return view_func(self, request, *args, **kwargs)
        return wrapper
    
    return decorator


def _check_password_verification_validity(request: HttpRequest, expiration_time_key: str) -> bool:
    """
    Checks if a request's user password identity verification is still valid.

    :param request: The request to check.
    :param expiration_time_key: The name of the key in the request session that 
    holds the password verification expiration time.
    """
    if not request.user.is_authenticated:
        return False
    
    expiration_time = request.session.get(expiration_time_key, None)
    if not expiration_time:
        return False
    expiration_time = dateutil_parser.parse(expiration_time)
    return expiration_time > timezone.now()


def requires_password_verification(
        view_func: Callable = None, 
        *, 
        verification_view: Callable | str = None,
        expiration_time_key: str = 'password_verification_expiration_time'
    ):
    """
    Decorator for views that ensures a user verifies identity with password before accessing the view.

    :param view_func: The view function to decorate.
    :param verification_view: The password verification view to redirect to. Could be a view, view name or url.
    Defaults to `settings.PASSWORD_VERIFICATION_VIEW`.
    :param expiration_time_key: The name of the key in the request session that 
    holds the password verification expiration time. Defaults to `password_verification_expiration_time`.

    The verification view should set the expiration time as `expiration_time_key` in the request session which will 
    define when the current verification expires and the user needs to re-verify.
    """

    def decorator(view_func: Callable[..., HttpResponse | JsonResponse]):
        """
        Ensures a user verifies identity with password before accessing decorated view.

        :param view_func: The view function to decorate.
        """
        @functools.wraps(view_func)
        def wrapper(view, request: HttpRequest, *args: str, **kwargs: Any):
            if _check_password_verification_validity(request, expiration_time_key):
                return view_func(view, request, *args, **kwargs)
            
            v_view = verification_view or getattr(settings, 'PASSWORD_VERIFICATION_VIEW', None)
            if not v_view:
                raise ValueError(
                    "A password verification view is required for password verification to work. "
                    "Either pass the `verification_view` keyword argument to the decorator or set `PASSWORD_VERIFICATION_VIEW` in settings."
                )
            verification_url = reverse(v_view)
            return redirect(f"{verification_url}?next={request.path}")
        return wrapper
    
    if view_func:
        return decorator(view_func)
    return decorator


