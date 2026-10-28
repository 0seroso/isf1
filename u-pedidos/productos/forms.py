from django import forms

from .models import Categoria, Producto


class FiltroCatalogoForm(forms.Form):
    categoria = forms.IntegerField(required=False, min_value=1, max_value=2**63 - 1)
    vendedor = forms.IntegerField(required=False, min_value=1, max_value=2**63 - 1)


class ProductoForm(forms.ModelForm):
    """Formulario para crear y editar productos; el vendedor se asigna en la vista."""

    precio = forms.IntegerField(
        label="Precio (CLP)",
        min_value=1,
        max_value=999999,
        widget=forms.NumberInput(attrs={"step": "1"}),
        help_text="Ingresa el precio en pesos enteros, por ejemplo 3500.",
        error_messages={
            "invalid": "Ingresa un precio en pesos enteros, sin decimales.",
            "min_value": "El precio debe ser mayor que 0.",
        },
    )

    categorias = forms.ModelMultipleChoiceField(
        queryset=Categoria.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Tipo de comida",
    )

    class Meta:
        model = Producto
        fields = [
            "nombre",
            "categorias",
            "precio",
            "stock",
            "imagen_url",
            "descripcion",
            "disponible",
        ]
        labels = {
            "nombre": "Nombre",
            "stock": "Unidades disponibles",
            "imagen_url": "Foto (enlace a la imagen)",
            "descripcion": "Descripción",
            "disponible": "Disponible para pedir",
        }
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "stock": forms.NumberInput(attrs={"min": 0}),
            "imagen_url": forms.URLInput(
                attrs={"placeholder": "https://ejemplo.com/foto.jpg"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        precio = self.initial.get("precio")
        if precio is not None and precio == int(precio):
            self.initial["precio"] = int(precio)
