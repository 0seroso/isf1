from django.urls import path

from . import views

app_name = "pedidos"

urlpatterns = [
    path("mis-pedidos/", views.MisPedidosView.as_view(), name="mis_pedidos"),
    path("<int:pk>/", views.DetallePedidoView.as_view(), name="detalle_pedido"),
    path("crear/", views.CrearPedidoView.as_view(), name="crear_pedido"),
]
