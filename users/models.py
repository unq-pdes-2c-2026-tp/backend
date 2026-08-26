from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from users.constants import UserType
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    user_type = models.PositiveSmallIntegerField(choices=UserType.choices)
    objects = UserManager()
    agency = models.ForeignKey("packages.Agency", on_delete=models.CASCADE, null=True)
    USERNAME_FIELD = "email"  # Identifies user via email
    REQUIRED_FIELDS = []  # Additional fields for createsuperuser
