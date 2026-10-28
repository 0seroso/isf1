from django import forms

from .models import Categoria, Producto


class FiltroCatalogoForm(forms.Form):
    categoria = forms.IntegerField(required=False, min_value=1, max_value=2**63 - 1)
    vendedor = forms.IntegerField(required=False, min_value=1, max_value=2**63 - 1)


class ProductoForm(forms.ModelForm):
    """Formulario para crear y editar productos; el vendedor se asigna en la vista."""

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
            "precio": "Precio ($)",
            "stock": "Unidades disponibles",
            "imagen_url": "Foto (enlace a la imagen)",
            "descripcion": "Descripción",
            "disponible": "Disponible para pedir",
        }
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "precio": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"min": 0}),
            "imagen_url": forms.URLInput(
                attrs={"placeholder": "https://ejemplo.com/foto.jpg"}
            ),
        }

    def clean_precio(self):
        """El precio debe ser mayor que cero."""
        precio = self.cleaned_data["precio"]
        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor que 0.")
        return precio
