from django.urls import path

from . import views

app_name = "pedidos"

urlpatterns = [
    path("crear/", views.CrearPedidoView.as_view(), name="crear_pedido"),
]