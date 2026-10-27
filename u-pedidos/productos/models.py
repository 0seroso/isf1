from django.conf import settings
from django.db import models


class Vendedor(models.Model):
    """Puesto de comida asociado a un usuario con rol vendedor"""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendedor",
        null=True,
        blank=True,
    )
    nombre = models.CharField(max_length=150)
    ubicacion = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    """Tipo de comida u opción alimentaria (vegano, sin gluten, bebidas...)"""

    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Producto que ofrece un vendedor; puede tener varias categorías"""

    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name="productos")
    categorias = models.ManyToManyField(Categoria, blank=True, related_name="productos")
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)
    imagen_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.vendedor.nombre})"