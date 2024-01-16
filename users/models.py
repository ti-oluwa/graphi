from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
from django.utils.translation import gettext_lazy as _
from django_utz.models.mixins import UTZUserModelMixin, UTZModelMixin
from timezone_field import TimeZoneField
from djmoney.models.fields import CurrencyField

from .managers import UserAccountManager


class UserAccount(UTZModelMixin, UTZUserModelMixin, PermissionsMixin, AbstractBaseUser):
    """Custom user model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(_("email address"), unique=True)
    timezone = TimeZoneField(_("timezone"), default="Africa/Lagos", help_text=_("Choose your timezone."))
    preferred_currency = CurrencyField(_("preferred currency"), default="NGN")
    is_active = models.BooleanField(_("active") ,default=True)
    is_admin = models.BooleanField(_("admin") ,default=False)
    is_staff = models.BooleanField(_("staff") ,default=False)
    is_superuser = models.BooleanField(_("superuser") ,default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ("firstname", "lastname")

    objects = UserAccountManager()

    user_timezone_field = "timezone"
    datetime_fields = ["registered_at", "updated_at"]

    class Meta:
        verbose_name = _("useraccount")
        verbose_name_plural = _("useraccounts")
    

    def __str__(self) -> str:
        return self.email
    
    @property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"
    
    @property
    def initials(self):
        return f"{self.firstname[0]}{self.lastname[0]}"


    def send_verification_email(self):
        """Send verification email to user."""
        pass    
