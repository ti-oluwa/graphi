import random
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
from typing import Any
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_utz.decorators import model, usermodel
from timezone_field import TimeZoneField
from djmoney.models.fields import CurrencyField
from django.core.mail import EmailMessage, get_connection as get_smtp_connection
from django.urls import reverse
from django.template.loader import render_to_string

from .managers import UserAccountManager



@model
@usermodel
class UserAccount(PermissionsMixin, AbstractBaseUser):
    """Custom user model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True, blank=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(_("email address"), unique=True)
    timezone = TimeZoneField(_("timezone"), default="Africa/Lagos", help_text=_("Choose your timezone."))
    preferred_currency = CurrencyField(_("preferred currency"), default="NGN")
    is_active = models.BooleanField(_("active") ,default=True)
    is_admin = models.BooleanField(_("admin") ,default=False)
    is_staff = models.BooleanField(_("staff") ,default=False)
    is_superuser = models.BooleanField(_("superuser") ,default=False)
    is_verified = models.BooleanField(_("verified") ,default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ("firstname", "lastname")

    objects = UserAccountManager()

    class Meta:
        verbose_name = _("user account")
        verbose_name_plural = _("user accounts")
    
    class UTZMeta:
        timezone_field = "timezone"
        datetime_fields = "__all__"
    

    def __str__(self) -> str:
        return self.email
    
    @property
    def fullname(self):
        return f"{self.firstname} {self.lastname}"
    
    @property
    def initials(self):
        return f"{self.firstname[0]}{self.lastname[0]}"
    

    def save(self, *args, **kwargs) -> None:
        """Save user account."""
        if not self.username:
            self.username = slugify(f'{self.firstname}{self.lastname}{random.randrange(00000, 99999)}')[:100]
        return super().save(*args, **kwargs)
    

    def send_mail(
            self, 
            subject: str, 
            message: str, 
            from_email: str = settings.DEFAULT_FROM_EMAIL, 
            connection: Any | None = None,
            html: bool = False
        ) -> None:
        """
        Send email to user.
        
        :param subject: The subject of the email.
        :param message: The message to send.
        :param from_email: The email address to send from.
        :param connection: The email connection to use.
        :param html: Whether the message is an html message.
        """
        connection = connection or get_smtp_connection()
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=f"Graphi <{from_email}>",
            to=[self.email],
            connection=connection
        )
        email.send(fail_silently=False)
        if html:
            email.content_subtype = "html"
        return None


    def send_verification_email(self) -> None:
        """Send verification email to user."""
        if self.is_verified:
            return
        subject = "Graphi - Verify your email address"
        body = construct_verification_email(self)
        return self.send_mail(subject, body, html=True)

    

def construct_verification_email(user: UserAccount) -> str:
    """Construct the verification email body."""
    verification_link = f"{settings.BASE_URL}/{reverse('users:account_verification', kwargs={'token': user.id.hex})}"
    context = {
        "username": user.firstname,
        "verification_link": verification_link,
        "current_year": timezone.now().year
    }
    return render_to_string("emails/verification_email.html", context)
