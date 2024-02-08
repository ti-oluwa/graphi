# from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import UserAccount


class UserCreationForm(UserCreationForm):
    """Form for creating a new user."""
    class Meta(UserCreationForm.Meta):
        model = UserAccount
        fields = (
            "firstname", "lastname", "email", 
            "timezone", "password1", "password2",
        )



class UserUpdateForm(UserChangeForm):
    """Form for updating a user's detail"""
    class Meta(UserChangeForm.Meta):
        model = UserAccount
        fields = (
            "firstname", "lastname", "email", 
            "timezone", "preferred_currency"
        )
