# from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import UserAccount


class UserCreationForm(UserCreationForm):
    """Form for creating a new user."""
    class Meta(UserCreationForm):
        model = UserAccount
        fields = (
            "firstname", "lastname", "email", 
            "timezone", "password1", "password2",
        )


