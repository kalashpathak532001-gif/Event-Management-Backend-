from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser to include an `is_admin`
    flag and enforce unique email addresses for authentication via email.
    """

    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.get_full_name() or self.email
