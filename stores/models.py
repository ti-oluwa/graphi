from django.db import models
import uuid
from django_utz.models.mixins import UTZModelMixin

class StoreType(models.TextChoices):
    """Choices for store types."""
    GROCERY = "grocery", "Grocery"
    PHARMACY = "pharmacy", "Pharmacy"
    RESTAURANT = "restaurant", "Restaurant"
    CLOTHING = "clothing", "Clothing"
    ELECTRONICS = "electronics", "Electronics"
    GIFT = "gift", "Gift"
    OTHER = "other", "Other"


class Store(UTZModelMixin, models.Model):
    """Model representing a store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=50, choices=StoreType.choices, default=StoreType.OTHER)
    email = models.EmailField(blank=True)
    owner = models.ForeignKey("users.UserAccount", on_delete=models.CASCADE, related_name="stores")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    datetime_fields = ("created_at", "updated_at")

    def __str__(self):
        return self.name
    
