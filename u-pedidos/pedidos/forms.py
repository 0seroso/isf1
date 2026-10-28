from datetime import datetime

from django import forms
from django.utils import timezone

from .franjas import validar_franja_reservable
from .models import Pedido


class FranjaRetiroField(forms.TimeField):
    """Convierte HH:MM en una franja de hoy que todavía no comienza."""

    input_formats = ("%H:%M",)

    def to_python(self, value):
        hora = super().to_python(value)
        if hora is None:
            return None
        return timezone.make_aware(datetime.combine(timezone.localdate(), hora))

    def validate(self, value):
        super().validate(value)
        if value is not None:
            validar_franja_reservable(value)


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
    retiro = FranjaRetiroField(
        label="Horario de retiro",
        error_messages={"required": "Elige un horario de retiro."},
    )


class FiltroPedidosForm(forms.Form):
    """Valida el estado recibido desde el filtro de Mis pedidos."""

    estado = forms.ChoiceField(
        label="Estado del pedido",
        required=False,
        choices=[("", "Todos los estados")] + Pedido.ESTADOS,
    )
