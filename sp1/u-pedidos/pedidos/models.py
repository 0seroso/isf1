from django.conf import settings
from django.db import models
from django.utils import timezone
from productos.models import Producto

class Pedido(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("listo", "Listo para retirar"),
        ("entregado", "Entregado"),
    ]
    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pedidos", null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Pedido #{self.id}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.producto.precio * self.cantidad
    