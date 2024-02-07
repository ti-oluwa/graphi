from django import forms

from .models import Product, ProductBrand, ProductGroup


class ProductForm(forms.ModelForm):
    """Form for creating and updating products."""
    class Meta:
        model = Product
        exclude = ("added_at", "updated_at")


class ProductBrandForm(forms.ModelForm):
    """Form for creating and updating products."""
    class Meta:
        model = ProductBrand
        exclude = ("created_at", "updated_at")


class ProductGroupForm(forms.ModelForm):
    """Form for creating and updating products."""
    class Meta:
        model = ProductGroup
        exclude = ("created_at", "updated_at")
