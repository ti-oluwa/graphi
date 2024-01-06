from typing import Any
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.generic import CreateView


from .forms import UserCreationForm
from .models import UserAccount


class UserCreateView(CreateView):
    """View for creating a user."""
    form_class = UserCreationForm
    template_name = "users/signup.html"
    success_url = "/signin/"

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> JsonResponse:
        """Handle POST requests."""
        form = self.form_class(request.data)
        if form.is_valid():
            user: UserAccount = form.save(commit=False)
            user.is_active = False
            user.save()
            user.send_verification_email()
            return JsonResponse(
                data={
                    "status": "success",
                    "redirect_url": self.success_url,
                },
                status=201
            )
            
        return JsonResponse(
            data={
                "status": "error",
                "errors": form.errors,
            },
            status=400
        )



user_create_view = UserCreateView.as_view()
