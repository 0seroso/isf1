from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """Usuario del sistema; el campo `rol` define si compra o vende."""

    ROLES = [
        ("vendedor", "Vendedor(a)"),
        ("comprador", "Comprador(a)"),
    ]
    rol = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return self.username