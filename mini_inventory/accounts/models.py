from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        MANAGER = "MANAGER", "Manager"
        CASHIER = "CASHIER", "Cashier"
        STOREKEEPER = "STOREKEEPER", "Storekeeper"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CASHIER,
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
    )

    def __str__(self):
        return self.get_full_name() or self.username