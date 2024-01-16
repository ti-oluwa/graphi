from django.db import models
import uuid
from django.http import HttpRequest
from datetime import timedelta
from django.utils import timezone

from django_utz.models.mixins import UTZModelMixin
from djmoney.models.fields import CurrencyField


class StoreTypes(models.TextChoices):
    """Choices for store types."""
    GROCERY = "grocery", "Grocery"
    MEDICAL = "medical", "Medical"
    MARKET = "market", "Market"
    MART = "mart", "Mart"
    MALL = "mall", "Mall"
    PROVISION = "provision", "Provision"
    PHARMACY = "pharmacy", "Pharmacy"
    RESTAURANT = "restaurant", "Restaurant"
    CLOTHING = "clothing", "Clothing"
    ELECTRONICS = "electronics", "Electronics"
    AUTO = "auto", "Auto"
    GIFT = "gift", "Gift"
    OTHER = "other", "Other"


class Store(UTZModelMixin, models.Model):
    """Model representing a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=50, choices=StoreTypes.choices, default=StoreTypes.OTHER)
    email = models.EmailField(blank=True)
    owner = models.ForeignKey("users.UserAccount", on_delete=models.CASCADE, related_name="stores")
    passkey = models.CharField(max_length=50, default=None, blank=True, null=True, editable=False)
    default_currency = CurrencyField(default="NGN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    datetime_fields = ["created_at", "updated_at"]

    class Meta:
        ordering = ("name", "-created_at")

    def __str__(self):
        return self.name
    

    def set_passkey(self, passkey: str) -> None:
        """Sets a passkey for this store."""
        if not isinstance(passkey, str):
            raise TypeError("Passkey must be a string.")
        if len(passkey) < 4:
            raise ValueError("Passkey must be at least 4 characters long.")
        self.passkey = passkey
        self.save()
    

    def authorize_request(self, request: HttpRequest, passkey: str) -> bool:
        """Authorizes a request to access this store."""
        if not request.user == self.owner:
            return False
        if not self.passkey:
            return True
        
        authorized = passkey == self.passkey
        if authorized:
            request.session["authorized_stores"] = [*request.session.get("authorized_stores", []), self.pk]
            expiry_time = timezone.now() + timedelta(day=1)
            request.session[f'authorization_for_store_{self.pk}_expires_at'] = expiry_time.strftime("%Y-%m-%d %H:%M:%S")
        return authorized


    def check_request_is_authorized(self, request: HttpRequest) -> bool:
        """Checks if a request is authorized to access this store."""
        if not request.user == self.owner:
            return False
        if not self.passkey:
            return True

        authorized_stores = request.session.get("authorized_stores", [])
        expiry_time = request.session.get(f'authorization_for_store_{self.pk}_expires_at')
        if not expiry_time:
            return False
        return self.pk in authorized_stores and timezone.now() < timezone.make_aware(expiry_time)
