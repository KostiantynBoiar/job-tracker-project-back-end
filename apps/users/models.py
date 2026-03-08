from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum


class AuthProvider(str, Enum):
    """Authentication provider choices."""
    EMAIL = 'email'
    GOOGLE = 'google'
    GITHUB = 'github'

    @classmethod
    def choices(cls):
        return [(c.value, c.value.capitalize()) for c in cls]


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.
    Uses email as the primary identifier.
    Supports both email/password and OAuth authentication.
    """
    email = models.EmailField(unique=True, blank=False, null=False)
    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices(),
        default=AuthProvider.EMAIL.value,
    )
    provider_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='User ID from OAuth provider (Google/GitHub)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def is_oauth_user(self):
        """Check if user registered via OAuth."""
        return self.auth_provider != AuthProvider.EMAIL.value
