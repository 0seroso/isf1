from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView

from productos.models import Producto
from usuarios.mixins import CompradorRequiredMixin
from .forms import FiltroPedidosForm
from .models import DetallePedido, Pedido


class PedidoCompradorMixin(LoginRequiredMixin, CompradorRequiredMixin):
    """La lista y el detalle solo pueden consultar pedidos del comprador actual."""

    model = Pedido

    def get_queryset(self):
        return (
            Pedido.objects.filter(comprador=self.request.user)
            .prefetch_related("items__producto__vendedor")
            .order_by("-fecha_creacion", "-pk")
        )


class MisPedidosView(PedidoCompradorMixin, ListView):
    template_name = "pedidos/mis_pedidos.html"
    context_object_name = "pedidos"

    def get_queryset(self):
        pedidos = super().get_queryset()
        self.form_filtros = FiltroPedidosForm(self.request.GET)
        if not self.form_filtros.is_valid():
            return pedidos.none()
        estado = self.form_filtros.cleaned_data["estado"]
        if estado:
            pedidos = pedidos.filter(estado=estado)
        return pedidos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_filtros"] = self.form_filtros
        return context


class DetallePedidoView(PedidoCompradorMixin, DetailView):
    template_name = "pedidos/detalle_pedido.html"
    context_object_name = "pedido"


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

        with transaction.atomic():
            # La base de datos comprueba y descuenta el stock en una sola operación.
            actualizados = Producto.objects.filter(
                pk=producto.pk,
                disponible=True,
                stock__gte=cantidad,
            ).update(stock=F("stock") - cantidad)
            if not actualizados:
                producto.refresh_from_db()
                if not producto.disponible or producto.stock <= 0:
                    messages.error(request, f"'{producto.nombre}' no se encuentra disponible actualmente.")
                else:
                    messages.error(
                        request,
                        f"No hay suficiente stock disponible de '{producto.nombre}' (Stock actual: {producto.stock}).",
                    )
                return redirect("productos:catalogo")

            producto.refresh_from_db()
            if producto.stock == 0:
                Producto.objects.filter(pk=producto.pk).update(disponible=False)

            pedido = Pedido.objects.create(
                comprador=request.user,
                estado="pendiente",
            )
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
            )

        ubicacion_retiro = (
            producto.vendedor.ubicacion.strip()
            if producto.vendedor.ubicacion
            else "Puesto del vendedor"
        )
        # La sesión guarda texto para conservar los centavos del Decimal.
        total_pedido = str(pedido.total())

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
