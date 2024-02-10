from django import forms

from .models import Sale


class SaleForm(forms.ModelForm):
    """Form for creating and updating sales."""
    class Meta:
        model = Sale
        fields = ("product", "quantity", "store", "payment_method")
