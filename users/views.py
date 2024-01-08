import json
from typing import Any
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import generic


from .forms import UserCreationForm
from .models import UserAccount
from .decorators import redirect_authenticated
from .utils import (
    get_products_count, get_stores_count
)



class UserDashboardView(LoginRequiredMixin, generic.TemplateView):
    """View for the user dashboard."""
    template_name = "users/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict:
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["stores_count"] = get_stores_count(self.request.user)
        context["products_count"] = get_products_count(self.request.user)
        return context



class UserCreateView(generic.CreateView):
    """View for creating a user."""
    form_class = UserCreationForm
    template_name = "users/signup.html"

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        data = json.loads(request.body.decode())
        form = self.get_form_class()(data)

        if form.is_valid():
            user: UserAccount = form.save(commit=False)
            user.is_active = False
            user.save()
            user.send_verification_email()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Account created successfully. Check your email for verification link.",
                    "redirect_url": reverse("signin")
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



class UserAuthenticationView(generic.TemplateView):
    """View for authenticating a user."""
    template_name = "users/signin.html"

    @redirect_authenticated("dashboard")
    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)


    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        data = json.loads(request.body.decode())
        email = data.get('email', None)
        password = data.get('password', None)
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": f"Welcome {user.fullname}!",
                    "redirect_url": reverse("dashboard")
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
 


class UserVerificationView(LoginRequiredMixin, generic.TemplateView):
    """View for verifying a user's account."""
    template_name = "users/verification.html"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        token = kwargs.get("token")
        user = UserAccount.objects.filter(pk=token).first()
        if user:
            user.is_active = True
            user.save()
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Account verified successfully!",
                    "redirect_url": reverse("signin")
                },
                status=200
            )
        
        return JsonResponse(
            data={
                "status": "error",
                "detail": "Invalid verification token!"
            },
            status=400
        )



class UserLogoutView(generic.RedirectView):
    """View for logging out a user."""
    url = "/signin/"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> None:
        if request.user.is_authenticated:
            logout(request)
        return super().get(request, *args, **kwargs)



user_dashboard_view = UserDashboardView.as_view()
user_create_view = UserCreateView.as_view()
user_auth_view = UserAuthenticationView.as_view()
user_verification_view = UserVerificationView.as_view()
user_logout_view = UserLogoutView.as_view()
