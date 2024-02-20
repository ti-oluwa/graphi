from __future__ import annotations
from typing import Any
from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserAccountManager(BaseUserManager):
    """Custom manager for `UserAccount` model."""
    use_in_migrations = True

    def create_user(self, email, password, save: bool = True, **extra_fields):
        if not email:
            raise ValueError("User must have an email!")
        if not password:
            raise ValueError("User must have a Password!")
        
        user = self.model(
            email=self.normalize_email(email=email),
            **extra_fields
        )
        
        user.set_password(password)
        if save is True:
            user.save(using=self._db)
        return user


    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(
            email=email,
            password=password,
            save=False,
            **extra_fields
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save(using=self._db)
        return user



class SearchableQuerySet(models.QuerySet):
    """A model queryset that supports search"""
    
    def search(self, query: str | Any, fields: list[str] | str) -> SearchableQuerySet:
        """
        Search the queryset for the given query in the given fields.

        :param query: The search query.
        :param fields: The fields to search in.
        :return: A queryset containing the search results.
        """
        if isinstance(fields, str):
            fields = [fields]

        query = query.strip()
        if not query:
            return self.none()
        
        q = models.Q()
        for field in fields:
            q = q | models.Q(**{f"{field}__icontains": query})
        return self.filter(q).distinct()



class SearchableModelManager(BaseUserManager.from_queryset(SearchableQuerySet)):

    def get_queryset(self) -> SearchableQuerySet:
        return super().get_queryset()
    
    
    def search(self, query: str | Any, fields: list[str] | str) -> SearchableQuerySet:
        """
        Search the model for the given query in the given fields.

        :param query: The search query.
        :param fields: The fields to search in.
        :return: A queryset containing the search results.
        """
        return self.get_queryset().search(query=query, fields=fields)
