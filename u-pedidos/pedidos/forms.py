from django import forms

from .models import Pedido


class FiltroPedidosForm(forms.Form):
    """Valida el estado recibido desde el filtro de Mis pedidos."""

    estado = forms.ChoiceField(
        label="Estado del pedido",
        required=False,
        choices=[("", "Todos los estados")] + Pedido.ESTADOS,
    )
