from django.db import models


class UserType(models.IntegerChoices):
    END_USER = 1, "Comprador"
    AGENCY = 2, "Agencia"
    ADMIN = 3, "Admin"
