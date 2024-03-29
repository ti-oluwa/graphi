from typing import Any, Callable
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
import functools
from django.utils import timezone
from django.conf import settings
from dateutil import parser as dateutil_parser

from .models import UserAccount


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
        verification_view: Callable | str = settings.PASSWORD_VERIFICATION_VIEW,
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
            
            v_view = verification_view
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


def requires_account_verification(
        view_func: Callable[..., HttpResponse | JsonResponse] = None,
        error_msg: str = "Account verification required!"
    ):
    """
    Ensures a user verifies account before accessing the view.

    :param view_func: The view function to decorate.
    :param error_msg: The error message to return if the user is not verified.
    """
    def decorator(view_func: Callable[..., HttpResponse | JsonResponse]):
        """
        Ensures a user verifies account before accessing decorated view.
        """
        @functools.wraps(view_func)
        def wrapper(view, request: HttpRequest, *args: str, **kwargs: Any):
            if request.user.is_verified:
                return view_func(view, request, *args, **kwargs)

            return HttpResponse(content=error_msg, status=403)
        return wrapper
    
    if view_func:
        return decorator(view_func)
    return decorator


def email_request_user_on_response(
        view_func: Callable[..., HttpResponse | JsonResponse] = None,
        *,
        status_code: int = 200,
        subject: str = None,
        body: str = None 
    ) -> Callable[..., HttpResponse | JsonResponse]:
    """
    Decorator that sends an email to the user on view response.

    :param view_func: The view function to decorate.
    :param status_code: The status code of the response to send the email on.
    :param subject: The subject of the email to send.
    :param body: The body of the email to send.
    """
    def decorator(view_func: Callable[..., HttpResponse | JsonResponse]):
        """
        Decorator that sends an email to the user on view response.
        """
        @functools.wraps(view_func)
        def wrapper(view, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse | JsonResponse:
            response = view_func(view, request, *args, **kwargs)
            sub = subject
            bod = body
            if not sub:
                sub = f"Request to {request.path}"
            if not bod:
                bod = f"Your request to {settings.BASE_URL}/{request.path} got response {response.status_code} - {response.reason_phrase}"
            if response.status_code == status_code:
                user: UserAccount = request.user
                try:
                    user.send_mail(sub, bod)
                except Exception:
                    pass
                
            return response
        return wrapper
    
    if view_func:
        return decorator(view_func)
    return decorator
    
