from django.db import models
import uuid
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from django.utils.translation import gettext_lazy as _
from django_utz.models.mixins import UTZModelMixin



class Product(UTZModelMixin, models.Model):
    """Model representing a product in a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = MoneyField(
        max_digits=10, decimal_places=2, 
        default_currency="NGN", 
        validators=[MinMoneyValidator(0.00)]
    )
    quantity = models.IntegerField(default=0)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)
    weight = models.DecimalField(_("Weight in grams"), max_digits=10, decimal_places=2, blank=True)
    group = models.ForeignKey("ProductGroup", blank=True, null=True, on_delete=models.SET_NULL, related_name="products")
    category = models.ForeignKey("ProductCategory", blank=True, null=True, on_delete=models.SET_NULL, related_name="products")
    brand = models.ForeignKey("ProductBrand", blank=True, null=True, on_delete=models.SET_NULL, related_name="products")
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="products")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    datetime_fields = ("added_at", "updated_at")

    def __str__(self):
        return self.name



class ProductCategory(UTZModelMixin, models.Model):
    """Model representing a product category in a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="product_categories")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    datetime_fields = ("created_at", "updated_at")

    def __str__(self):
        return self.name



class ProductGroup(UTZModelMixin, models.Model):
    """Model representing a product group in a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="product_groups")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    datetime_fields = ("created_at", "updated_at")

    def __str__(self):
        return self.name



class ProductBrand(UTZModelMixin, models.Model):
    """Model representing a product brand in a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="product_brands")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    datetime_fields = ("created_at", "updated_at")

    def __str__(self):
        return self.name
