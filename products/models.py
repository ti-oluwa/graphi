from __future__ import annotations

from django.db import models
import uuid
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from django.utils.translation import gettext_lazy as _
from django_utz.decorators import model
from decimal import Decimal


class ProductCategories(models.TextChoices):
    """Choices for product categories."""
    FASHION = "fashion", _("Fashion")
    ELECTRONICS = "electronics", _("Electronics")
    FOOD = "food", _("Food")
    BEAUTY = "beauty", _("Beauty")
    HEALTH = "health", _("Health")
    HOME = "home", _("Home")
    BOOKS = "books", _("Books")
    SPORTS = "sports", _("Sports")
    AUTOMOBILE = "automobile", _("Automobile")
    OTHERS = "others", _("Others")



@model
class Product(models.Model):
    """Model representing a product in a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = MoneyField(
        max_digits=14, 
        decimal_places=2, 
        default_currency="NGN", 
        default=Decimal("0.00"),
        validators=[MinMoneyValidator(Decimal("0.00"))]
    )
    quantity = models.IntegerField(default=0)
    color = models.CharField(max_length=50, blank=True)
    size = models.CharField(max_length=50, blank=True)
    weight = models.DecimalField(_("Weight in grams"), max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.CharField(max_length=50, choices=ProductCategories.choices, default=ProductCategories.OTHERS)
    group = models.ForeignKey("ProductGroup", blank=True, null=True, on_delete=models.SET_NULL, related_name="products")
    brand = models.ForeignKey("ProductBrand", blank=True, null=True, on_delete=models.SET_NULL, related_name="products")
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="products")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("name", "-added_at")
    
    class UTZMeta:
        datetime_fields = "__all__"


    def __str__(self):
        return self.name
    
    @property
    def last_sold_at(self):
        """The last date the product was sold"""
        latest_sale = self.sales.latest("made_at")
        return latest_sale.made_at if latest_sale else None
    

@model
class ProductGroup(models.Model):
    """Model representing a product group in a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="product_groups")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Group"
        verbose_name_plural = "Product Groups"
        ordering = ("name", "-created_at")
        unique_together = ("name", "store")

    class UTZMeta:
        datetime_fields = "__all__"

    def __str__(self):
        return self.name


@model
class ProductBrand(models.Model):
    """Model representing a product brand in a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    store = models.ForeignKey("stores.Store", on_delete=models.CASCADE, related_name="product_brands")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Brand"
        verbose_name_plural = "Product Brands"
        ordering = ("name", "-created_at")
        unique_together = ("name", "store")

    class UTZMeta:
        datetime_fields = "__all__"


    def __str__(self):
        return self.name
