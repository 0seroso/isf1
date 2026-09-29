from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from usuarios.mixins import CompradorRequiredMixin
from .models import Producto


class CatalogoView(LoginRequiredMixin, CompradorRequiredMixin, ListView):
    model = Producto
    template_name = "productos/catalogo.html"
    context_object_name = "productos"

    def get_queryset(self):
        return (Producto.objects.filter(disponible=True, stock__gt=0)
                .select_related("vendedor"))