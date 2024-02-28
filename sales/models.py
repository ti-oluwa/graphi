from __future__ import annotations

from typing import Any
import uuid
import random
import string
from django.db import models
from django_utz.decorators import model
from djmoney.money import Money
from djmoney.contrib.exchange.models import convert_money
from django.core.exceptions import ValidationError

from .managers import SaleManager



def generate_transaction_id() -> str:
    """Generates a unique transaction ID."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


class PaymentMethod(models.TextChoices):
    """Choices for payment methods."""
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    BANK_TRANSFER = "bank transfer", "Bank Transfer"



@model
class Sale(models.Model):
    """Model for a product sale."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(max_length=100, default=generate_transaction_id, unique=True)
    store = models.ForeignKey(
        "stores.Store", on_delete=models.CASCADE, related_name="sales"
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="sales"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH
    )
    made_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SaleManager()

    class Meta:
        verbose_name = "sale"
        verbose_name_plural = "sales"
        ordering = ("-made_at",)

    class UTZMeta:
        datetime_fields = "__all__"


    @property
    def revenue(self) -> Money:
        """Returns the total amount made from the sale."""
        return self.quantity * self.product.price

    @property
    def currency(self) -> str:
        """Returns the currency used to make the sale."""
        return self.amount.currency

    
    def __str__(self) -> str:
        return f"{self.store.name} - {self.product.name} - {self.quantity} - {self.revenue}"


    def __add__(self, other: Sale) -> Money:
        """
        Add the revenue of one sale to another.

        Returns the sum of the revenue in the currency of the first sale.
        """
        if not isinstance(other, Sale):
            raise ValueError("Cannot add a sale to a non-sale object")
        if other.revenue.currency != self.revenue.currency:
            other.revenue = convert_money(other.revenue, self.revenue.currency)
        return self.revenue + other.revenue
    
    __iadd__ = __add__
    __radd__ = __add__
    

    def __sub__(self, other: Sale) -> Money:
        """
        Subtract the revenue of one sale from another.

        Returns the difference in revenue in the currency of the first sale.
        """
        if not isinstance(other, Sale):
            raise ValueError("Cannot subtract a sale from a non-sale object")
        if other.revenue.currency != self.revenue.currency:
            other.revenue = convert_money(other.revenue, self.revenue.currency)
        return self.revenue - other.revenue
    
    __isub__ = __sub__
    __rsub__ = __sub__


    def save(self, *args: str, **kwargs: Any) -> None:
        """Save the sale."""
        if self.quantity == 0:
            raise ValidationError("Sale quantity cannot be zero")
        
        try:
            # If the sale is being updated, add the old sale quantity back to the product quantity
            old_sale = Sale.objects.get(pk=self.pk)
            self.product.quantity += old_sale.quantity
        except Sale.DoesNotExist:
            pass

        if self.quantity > self.product.quantity:
            raise ValidationError(f"Sale quantity cannot be greater than available product quantity ({self.product.quantity})")
        
        self.product.quantity -= self.quantity
        # Save the sale first before saving the product. This is to avoid reducing the product quantity
        # without a corresponding sale.
        super().save(*args, **kwargs)
        self.product.save()

    
    def delete(self, *args: str, **kwargs: Any) -> None:
        """Delete the sale."""
        self.product.quantity += self.quantity
        super().delete(*args, **kwargs)
        self.product.save()


    @classmethod
    def get_total_revenue(cls, currency, **filter) -> Money:
        """
        Returns the total revenue made from all sales based on the filter.

        :param currency: Currency to get the revenue in.
        :param filter: Filter to apply to the sales.
        """
        return sum(
            map(lambda sale: convert_money(sale.revenue, currency), cls.objects.filter(**filter))
        ) or Money(0, currency)


    @classmethod
    def get_count(cls, **filters) -> int:
        """
        Returns the number of sales based on the filter.

        :param filter: Filter to apply to the sales.
        """
        return cls.objects.filter(**filters).count()
