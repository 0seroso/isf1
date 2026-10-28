from django.contrib import admin
from pedidos.models import DetallePedido, Pedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "comprador", "estado", "fecha_creacion", "retiro_inicio")
    list_filter = ("estado", "retiro_inicio")


admin.site.register(DetallePedido)
