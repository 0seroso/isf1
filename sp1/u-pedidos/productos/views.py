from django.views.generic import ListView
from .models import Producto


class CatalogoView(ListView):
    model = Producto
    template_name = "productos/catalogo.html"
    context_object_name = "productos"