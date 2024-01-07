import json
from typing import Any
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.http import HttpRequest, JsonResponse
from django.views import generic


from .forms import UserCreationForm
from .models import UserAccount


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
    template_name = "users/signin.html"

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        data = json.loads(request.body.decode())
        user = authenticate(request, **data)
        if user:
            login(request, user)
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": f"Welcome {user.fullname}!",
                    "redirect_url": ""
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
 


user_create_view = UserCreateView.as_view()
user_auth_view = UserAuthenticationView.as_view()
