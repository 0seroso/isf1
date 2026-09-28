from django import forms
from django.contrib.auth.forms import UserCreationForm

from productos.models import Vendedor

from .models import Usuario


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    rol = forms.ChoiceField(
        choices=Usuario.ROLES,
        widget=forms.Select,
        required=True,
    )

    class Meta:
        model = Usuario
        fields = ("username", "email", "rol", "password1", "password2")


class PerfilVendedorForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = ("nombre", "ubicacion")
