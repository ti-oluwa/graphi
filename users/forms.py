# from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import TallyUser


class TallyUserCreationForm(UserCreationForm):
    """Form for creating a new user."""
    class Meta(UserCreationForm):
        model = TallyUser
        fields = (
            "firstname", "lastname", "email", 
            "timezone", "password1", "password2",
        )


