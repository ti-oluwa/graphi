import json
from typing import Any, Dict
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views import generic
from django.conf import settings

from .forms import UserCreationForm
from .models import UserAccount
from products.models import ProductCategories
from .decorators import redirect_authenticated
from stores.utils import get_stores_count
from products.utils import get_products_count
from sales.utils import aggregate_sales_count, aggregate_revenue_from_sales
from .utils import parse_query_params_from_request


class UserIndexView(generic.RedirectView):
    """View for redirecting to the user dashboard."""
    url = "/dashboard/"



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
            user.is_active = False
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
                    "detail": "Account created successfully. Check your email for verification link.",
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

    @redirect_authenticated("users:dashboard")
    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)


    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles user authentication AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        email = data.get('email', None)
        password = data.get('password', None)
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": f"Welcome {user.fullname}!",
                    "redirect_url": reverse("users:dashboard")
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
 


class UserVerificationView(LoginRequiredMixin, generic.View):
    """View for verifying a user's account."""
    # template_name = "users/verification.html"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        token = kwargs.get("token")
        if not request.user.id.hex == token:
            return HttpResponse(
            content="Invalid verification link!",
            status=400
        )
        
        if request.user.is_active:
            return HttpResponse(
                content="Your account has already been verified!",
                status=200
            )
        
        request.user.is_active = True
        request.user.save()
        return HttpResponse(
            content="Your account has been verified successfully!",
            status=200
        )



class UserLogoutView(generic.RedirectView):
    """View for logging out a user."""
    url = "/signin/"

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



class DashboardView(LoginRequiredMixin, generic.TemplateView):
    """View for the user dashboard."""
    template_name = "users/dashboard.html"
    http_method_names = ["get"]

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["stores_count"] = get_stores_count(self.request.user)
        context["products_count"] = get_products_count(self.request.user)
        context["sales_count"] = aggregate_sales_count(self.request.user)
        context["revenue_from_sales"] = aggregate_revenue_from_sales(self.request.user)
        context["product_categories"] = ProductCategories.labels
        return context
    


class DashboardStatisticsView(LoginRequiredMixin, generic.View):
    """View for retrieving dashboard statistics."""
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handles dashboard statistics AJAX/Fetch POST request"""
        data: Dict = json.loads(request.body)
        stat_type = data.pop("stat_type", None)

        if stat_type == "sales":
            result = aggregate_sales_count(self.request.user, **data)
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Sales statistics retrieved successfully!",
                    "data": {
                        "result": result
                    }
                },
                status=200
            )
        
        elif stat_type == "revenue":
            result = aggregate_revenue_from_sales(self.request.user, **data)
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Revenue statistics retrieved successfully!",
                    "data": {
                        "result": f'{result.currency} {result.amount}'
                    }
                },
                status=200
            )
        
        return JsonResponse(
            data={
                "status": "error",
                "detail": f"Invalid statistics type: {stat_type}"
            },
            status=400
        )


user_index_view = UserIndexView.as_view()
user_create_view = UserCreateView.as_view()
user_login_view = UserLoginView.as_view()
user_verification_view = UserVerificationView.as_view()
user_logout_view = UserLogoutView.as_view()
password_verification_view = UserPasswordVerificationView.as_view()
dashboard_view = DashboardView.as_view()
dashboard_stats_view = DashboardStatisticsView.as_view()
