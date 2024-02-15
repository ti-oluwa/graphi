import json
import random
from typing import Any, Dict
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views import generic
from django.conf import settings
import functools
from urllib.parse import urlencode as urllib_urlencode
from djmoney.settings import CURRENCY_CHOICES
import pytz

from .forms import UserCreationForm, UserUpdateForm
from .models import UserAccount
from .decorators import (
    redirect_authenticated, requires_password_verification, 
    requires_account_verification, email_request_user_on_response
)
from stores.decorators import to_JsonResponse
from .utils import parse_query_params_from_request



class UserCreateView(generic.CreateView):
    """View for creating a user."""
    form_class = UserCreationForm
    template_name = "users/signup.html"

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles user creation AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        form = self.get_form_class()(data)

        if form.is_valid():
            user: UserAccount = form.save(commit=False)
            try:
                user.send_verification_email()
            except Exception:
                return JsonResponse(
                    data={
                        "status": "error",
                        "detail": "Failed to send verification email! Please try again!"
                    },
                    status=500
                )
            
            user.save()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Account created successfully. Check your email for a verification link.",
                    "redirect_url": reverse("users:signin")
                },
                status=201
            )

        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred while creating account!",
                "errors": form.errors,
            },
            status=400
        )



class UserLoginView(generic.TemplateView):
    """View for authenticating a user."""
    template_name = "users/signin.html"

    @redirect_authenticated("dashboard:dashboard")
    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)


    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles user authentication AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        email = data.get('email', None)
        password = data.get('password', None)
        current_timezone = data.get('timezone', None)
        
        user = authenticate(request, username=email, password=password)
        if user:
            if current_timezone:
                user.timezone = current_timezone
                user.save()
            login(request, user)
            
            query_params = parse_query_params_from_request(request)
            next_url = query_params.pop("next", None) 
            if next_url and query_params:
                other_query_params = urllib_urlencode(query_params)
                next_url = f"{next_url}?{other_query_params}"
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": f"Welcome {user.fullname}!",
                    "redirect_url": next_url or reverse("dashboard:dashboard")
                },
                status=200
            )
        
        return JsonResponse(
            data={
                "status": "error",
                "detail": "Incorrect email or password!"
            },
            status=400
        )
 


class UserAccountVerificationView(LoginRequiredMixin, generic.TemplateView):
    """View for verifying a user's account."""
    template_name = "users/user_verification.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        token = self.kwargs.get("token", None)
        if token != self.request.user.id.hex:
            context["verification_status"] = "error"
            context["verification_detail"] = "Invalid verification link!"
        else:
            self.request.user.is_verified = True
            self.request.user.save()
            context["verification_status"] = "success"
            context["verification_detail"] = "Your account has been verified successfully!"
        return context
    

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        if request.user.is_verified:
            return redirect("users:dashboard")
        return super().get(request, *args, **kwargs)



class UserLogoutView(generic.RedirectView):
    """View for logging out a user."""
    url = "/accounts/signin/"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> None:
        if request.user.is_authenticated:
            logout(request)
        return super().get(request, *args, **kwargs)



class UserPasswordVerificationView(LoginRequiredMixin, generic.TemplateView):
    """
    View for verifying a user's password.

    Verifies user for period defined in `settings.PASSWORD_VERIFICATION_VALIDITY_PERIOD`
    """
    http_method_names = ["get", "post"]
    template_name = 'users/password_verification.html'

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles password verification AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        query_params = parse_query_params_from_request(request)
        next_url = query_params.get("next", None)
        if not next_url:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Invalid Request URL! Expected a query parameter named 'next' but none was found."
                },
                status=400
            )

        password = data.get("password", None)
        if not password:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Password not provided!"
                },
                status=400
            )

        password_ok = request.user.check_password(password)
        if password_ok:
            expiration_time = timezone.now() + timezone.timedelta(seconds=settings.PASSWORD_VERIFICATION_VALIDITY_PERIOD)
            request.session["password_verification_expiration_time"] = expiration_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Password verified successfully!",
                    "redirect_url": next_url
                },
                status=200
            )
        
        return JsonResponse(
            data={
                "status": "error",
                "detail": "Incorrect password!"
            },
            status=400
        )



class UserAccountDetailView(LoginRequiredMixin, generic.DetailView):
    """View for getting a user's account details."""
    model = UserAccount
    template_name = "users/user_account.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "user"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["currencies"] = CURRENCY_CHOICES
        context["timezones"] = pytz.all_timezones
        return context
    

    @requires_password_verification
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)



class UserAccountPasswordChangeView(LoginRequiredMixin, generic.DetailView):
    """View for changing a user's password."""
    model = UserAccount
    http_method_names = ["post"]
    slug_field = "username"
    slug_url_kwarg = "username"

    subject = "Graphi - Account Password Change"
    body = "Your Graphi account password has been changed successfully.\n\n If you did not make this change, please contact us immediately."

    email_request_user_on_password_change = functools.partial(email_request_user_on_response, subject=subject, body=body)

    @email_request_user_on_password_change
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles user password change AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        user: UserAccount = self.get_object()
        current_password = data.get("old-password", None)
        new_password = data.get("new-password1", None)
        confirm_password = data.get("new-password2", None)

        if not current_password:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Current password not provided!"
                },
                status=400
            )

        if not new_password:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "New password not provided!"
                },
                status=400
            )
        
        if current_password == new_password:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "New password cannot be the same as the current password!"
                },
                status=400
            )

        if new_password != confirm_password:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "New password and confirm password do not match!"
                },
                status=400
            )

        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Password changed successfully!"
                },
                status=200
            )
        
        return JsonResponse(
            data={
                "status": "error",
                "detail": "Incorrect current password!"
            },
            status=400
        )



class UserAccountUpdateView(LoginRequiredMixin, generic.UpdateView):
    """View for updating a user's account details."""
    model = UserAccount
    form_class = UserUpdateForm
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "user"
    http_method_names = ["post"]

    @to_JsonResponse
    @requires_account_verification
    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles user detail update AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        user = self.get_object()
        form = self.get_form_class()(data=data, instance=user)

        if form.is_valid():
            user: UserAccount = form.save(commit=False)
            extra_msg = ""
            if "email" in form.changed_data:
                user.is_verified = False
                try:
                    user.send_verification_email()
                    extra_msg = "You'll need to verify your new email. Please check your email inbox for a verification link."
                except Exception:
                    return JsonResponse(
                        data={
                            "status": "error",
                            "detail": "Failed to send verification email on email update! Please try again!"
                        },
                        status=400
                    )
            
            user.save()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": f"Account update successfully! {extra_msg}",
                },
                status=200
            )

        return JsonResponse(
            data={
                "status": "error",
                "detail": "An error occurred while updating account!",
                "errors": form.errors,
            },
            status=400
        )


class UserAccountDeleteView(LoginRequiredMixin, generic.DetailView):
    """View for deleting a sale record from a store."""
    model = UserAccount
    http_method_names = ["get"]
    slug_field = "username"
    slug_url_kwarg = "username"

    @requires_password_verification(expiration_time_key=f"{random.randrange(0000000, 9999999)}")
    # Changed the expiration time key so that the user cannot 
    # delete his/her account without password verifying again
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return redirect("users:signin")



class StoreReportRedirectView(LoginRequiredMixin, generic.RedirectView):
    """View for redirecting to a store's sales report page from the account management page."""
    permanent = False
    pattern_name = "stores:reports:sales_report"

    def get_redirect_url(self, *args, **kwargs) -> str:
        store_slug = self.request.GET.get("store", None)
        if store_slug:
            redirect_url = reverse(self.pattern_name, kwargs={"store_slug": store_slug})
            todays_date = self.request.user.to_local_timezone(timezone.now()).date()
            return f"{redirect_url}?date={todays_date}"
        return reverse("dashboard:dashboard")



# Account creation and verification
user_create_view = UserCreateView.as_view()
user_login_view = UserLoginView.as_view()
account_verification_view = UserAccountVerificationView.as_view()
user_logout_view = UserLogoutView.as_view()
password_verification_view = UserPasswordVerificationView.as_view()


# Account management
user_account_view = UserAccountDetailView.as_view()
user_account_password_change_view = UserAccountPasswordChangeView.as_view()
user_account_update_view = UserAccountUpdateView.as_view()
user_account_delete_view = UserAccountDeleteView.as_view()

# Store report redirect
store_report_redirect_view = StoreReportRedirectView.as_view()

