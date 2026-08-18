from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from users.constants import UserType
from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    user_type = models.PositiveSmallIntegerField(choices=UserType.choices)
    objects = UserManager()
    USERNAME_FIELD = 'email' # Identifies user via email
    REQUIRED_FIELDS = [] # Additional fields for createsuperuser
