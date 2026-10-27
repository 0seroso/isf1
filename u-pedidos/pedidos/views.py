from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from productos.models import Producto
from usuarios.mixins import CompradorRequiredMixin
from .models import DetallePedido, Pedido


class CrearPedidoView(LoginRequiredMixin, CompradorRequiredMixin, View):
    """Crea un pedido para un producto seleccionado por un comprador desde el catálogo."""

    def post(self, request, *args, **kwargs):
        producto_id = request.POST.get("producto_id")
        cantidad_str = request.POST.get("cantidad", "1")

        producto = get_object_or_404(Producto, pk=producto_id)

        try:
            cantidad = int(cantidad_str)
            if cantidad <= 0:
                raise ValueError()
        except ValueError:
            messages.error(request, "La cantidad solicitada debe ser un número entero mayor a 0.")
            return redirect("productos:catalogo")

        if not producto.disponible or producto.stock <= 0:
            messages.error(request, f"'{producto.nombre}' no se encuentra disponible actualmente.")
            return redirect("productos:catalogo")

        if cantidad > producto.stock:
            messages.error(
                request,
                f"No hay suficiente stock disponible de '{producto.nombre}' (Stock actual: {producto.stock}).",
            )
            return redirect("productos:catalogo")

        with transaction.atomic():
            pedido = Pedido.objects.create(
                comprador=request.user,
                estado="pendiente",
            )
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
            )
            producto.stock -= cantidad
            if producto.stock == 0:
                producto.disponible = False
            producto.save()

        ubicacion_retiro = (
            producto.vendedor.ubicacion.strip()
            if producto.vendedor.ubicacion
            else "Puesto del vendedor"
        )
        total_pedido = int(pedido.total())

        request.session["reserva_confirmada"] = {
            "pedido_id": pedido.id,
            "producto": producto.nombre,
            "cantidad": cantidad,
            "total": total_pedido,
            "vendedor": producto.vendedor.nombre,
            "ubicacion": ubicacion_retiro,
        }

        messages.success(
            request,
            f"¡Reserva #{pedido.id} confirmada con éxito! Punto de retiro: {ubicacion_retiro}.",
        )
        return redirect("productos:catalogo")
