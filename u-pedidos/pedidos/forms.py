from django import forms

from .models import Pedido


class CrearPedidoForm(forms.Form):
    producto_id = forms.IntegerField(
        min_value=1,
        max_value=2**63 - 1,
        widget=forms.HiddenInput,
        error_messages={
            "required": "Selecciona un producto válido del catálogo.",
            "invalid": "Selecciona un producto válido del catálogo.",
            "min_value": "Selecciona un producto válido del catálogo.",
            "max_value": "Selecciona un producto válido del catálogo.",
        },
    )
    cantidad = forms.IntegerField(
        min_value=1,
        max_value=2**31 - 1,
        error_messages={
            "required": "La cantidad solicitada debe ser un número entero mayor a 0.",
            "invalid": "La cantidad solicitada debe ser un número entero mayor a 0.",
            "min_value": "La cantidad solicitada debe ser un número entero mayor a 0.",
            "max_value": "La cantidad solicitada es demasiado grande.",
        },
    )


class FiltroPedidosForm(forms.Form):
    """Valida el estado recibido desde el filtro de Mis pedidos."""

    estado = forms.ChoiceField(
        label="Estado del pedido",
        required=False,
        choices=[("", "Todos los estados")] + Pedido.ESTADOS,
    )
