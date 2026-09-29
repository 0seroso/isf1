from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from usuarios.mixins import CompradorRequiredMixin
from .models import Categoria, Producto, Vendedor


class CatalogoView(LoginRequiredMixin, CompradorRequiredMixin, ListView):
    model = Producto
    template_name = "productos/catalogo.html"
    context_object_name = "productos"

    def get_queryset(self):
        productos = (Producto.objects.filter(disponible=True, stock__gt=0)
                     .select_related("vendedor", "categoria"))
        categoria = self.request.GET.get("categoria", "")
        if categoria.isdigit():
            productos = productos.filter(categoria_id=int(categoria))
        vendedor = self.request.GET.get("vendedor", "")
        if vendedor.isdigit():
            productos = productos.filter(vendedor_id=int(vendedor))
        return productos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categoria = self.request.GET.get("categoria", "")
        vendedor = self.request.GET.get("vendedor", "")
        context["categorias"] = Categoria.objects.all()
        context["vendedores"] = Vendedor.objects.all()
        context["categoria_actual"] = int(categoria) if categoria.isdigit() else None
        context["vendedor_actual"] = int(vendedor) if vendedor.isdigit() else None
        return context