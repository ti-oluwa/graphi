from django.conf.locale import he
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
    signature = models.CharField(
        max_length=50, default=uuid.uuid4().hex, blank=True, null=True, editable=False,
        help_text="A unique string that identifies this store apart from its primary key. It is used in store access authorization."
    )
    default_currency = CurrencyField(default="NGN")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    datetime_fields = ["created_at", "updated_at"]

    class Meta:
        ordering = ("name", "-created_at")

    def __str__(self):
        return self.name
    

    def change_signature(self) -> None:
        """
        Changes the signature of this store.

        Changing the signature invalidates previous authorizations.
        """
        self.signature = uuid.uuid4().hex
        return None
    
    
    def set_passkey(self, passkey: str) -> None:
        """
        Sets a passkey for this store.
        
        The change made by this method is not saved to the database.
        Call `save()` on the store instance to save the change to the database.
        """
        if not isinstance(passkey, str):
            raise TypeError("Passkey must be a string.")
        if len(passkey) < 4:
            raise ValueError("Passkey must be at least 4 characters long.")
        self.passkey = passkey
        self.change_signature()
        return None
    

    def authorize_request(self, request: HttpRequest, passkey: str) -> bool:
        """Authorizes a request to access this store."""
        if not request.user == self.owner:
            return False
        # If the store has no passkey, it is always authorized.
        if not self.passkey:
            return True
        
        authorized = passkey == self.passkey
        if authorized:
            expiry_time = timezone.now() + timedelta(days=1)
            request.session[f'authorization_for_store_{self.signature}_expires_at'] = expiry_time.strftime("%Y-%m-%d %H:%M:%S")
        return authorized


    def revoke_authorization(self, request: HttpRequest) -> None:
        """Revokes authorization for a request to access this store."""
        if not request.user == self.owner:
            return
        if not self.passkey:
            return
        request.session.pop(f'authorization_for_store_{self.signature}_expires_at', None)
        return None


    def check_request_is_authorized(self, request: HttpRequest) -> bool:
        """Checks if a request is authorized to access this store."""
        if not request.user == self.owner:
            return False
        # If the store has no passkey, it is always authorized.
        if not self.passkey:
            return True

        expiry_time = request.session.get(f'authorization_for_store_{self.signature}_expires_at')
        if not expiry_time:
            self.revoke_authorization(request)
            return False
        
        expiry_time = timezone.datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S")
        return timezone.now() < timezone.make_aware(expiry_time)
