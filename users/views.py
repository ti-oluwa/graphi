from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView


from .forms import TallyUserCreationForm


class UserCreateView(CreateView):
    """View for creating a user."""
    form_class = TallyUserCreationForm
    template_name = "users/signup.html"
    success_url = "/"

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        """Handle POST requests."""
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save(commit=False)
            return self.form_valid(form)
        return self.form_invalid(form)



user_create_view = UserCreateView.as_view()
