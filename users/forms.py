# from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserCreationForm(UserCreationForm):
    """Form for creating a new user."""
    class Meta(UserCreationForm):
        model = User
        fields = (
            "firstname", "lastname", "email", 
            "timezone", "password1", "password2",
        )


