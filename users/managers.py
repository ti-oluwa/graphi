from django.contrib.auth.models import BaseUserManager


class TallyUserManager(BaseUserManager):
    """Custom manager for `TallyUser` model."""
    use_in_migrations = True

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("User must have an email!")
        if not password:
            raise ValueError("User must have a Password!")
        
        user = self.model(
            email=self.normalize_email(email=email),
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(
            email=email,
            password=password,
            **extra_fields
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    



