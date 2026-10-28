from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from productos.models import Producto

from .franjas import DURACION_FRANJA, validar_inicio_de_franja


class Pedido(models.Model):
    """Pedido de una persona compradora; avanza por los estados de ESTADOS"""

    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("en_preparacion", "En preparación"),
        ("listo", "Listo para retirar"),
        ("entregado", "Entregado"),
    ]
    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pedidos", null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    retiro_inicio = models.DateTimeField(
        "inicio de la franja de retiro",
        null=True,
        blank=True,
    )

    @property
    def retiro_fin(self) -> datetime | None:
        """Fin de la franja; los pedidos anteriores pueden no tener horario."""
        if self.retiro_inicio is None:
            return None
        return self.retiro_inicio + DURACION_FRANJA

    def clean(self):
        """Valida la franja sin impedir la edición de pedidos antiguos."""
        super().clean()
        if self.retiro_inicio is not None:
            try:
                validar_inicio_de_franja(self.retiro_inicio)
            except ValidationError as error:
                raise ValidationError({"retiro_inicio": error}) from error

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Pedido #{self.id}"


class DetallePedido(models.Model):
    """Línea de un pedido: un producto y la cantidad pedida"""

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def subtotal(self):
        return self.precio_unitario * self.cantidad
