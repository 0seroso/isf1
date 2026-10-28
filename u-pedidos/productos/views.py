from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from pedidos.franjas import franjas_reservables
from usuarios.mixins import CompradorRequiredMixin, VendedorRequiredMixin
from .forms import FiltroCatalogoForm, ProductoForm
from .models import Categoria, Producto, Vendedor


class CatalogoView(LoginRequiredMixin, CompradorRequiredMixin, ListView):
    """Catálogo de productos disponibles, visible solo para compradores."""

    model = Producto
    template_name = "productos/catalogo.html"
    context_object_name = "productos"

    def get_queryset(self):
        """Productos disponibles, filtrados por categoría y vendedor si vienen en la URL."""
        productos = (
            Producto.objects.filter(disponible=True, stock__gt=0)
            .select_related("vendedor")
            .prefetch_related("categorias")
        )
        self.form_filtros = FiltroCatalogoForm(self.request.GET)
        if not self.form_filtros.is_valid():
            messages.error(
                self.request,
                "Los filtros recibidos no son válidos. Vuelve a elegir el puesto o la categoría.",
            )
            return productos.none()
        categoria = self.form_filtros.cleaned_data["categoria"]
        vendedor = self.form_filtros.cleaned_data["vendedor"]
        if categoria is not None:
            productos = productos.filter(categorias__id=categoria)
        if vendedor is not None:
            productos = productos.filter(vendedor_id=vendedor)
        return productos.distinct()

    def get_context_data(self, **kwargs):
        """Agrega categorías, vendedores y filtros activos para el template."""
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.all()
        context["vendedores"] = Vendedor.objects.all()
        context["franjas_retiro"] = franjas_reservables()
        context["form_filtros"] = self.form_filtros
        context["categoria_actual"] = self.form_filtros.cleaned_data.get("categoria")
        context["vendedor_actual"] = self.form_filtros.cleaned_data.get("vendedor")
        context["reserva_confirmada"] = self.request.session.pop("reserva_confirmada", None)
        return context
    
    
class ProductoVendedorMixin(LoginRequiredMixin, VendedorRequiredMixin):
    """Base para las vistas de gestión: solo vendedores con perfil, y solo sus productos."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol == "vendedor":
            self.vendedor = Vendedor.objects.filter(usuario=request.user).first()
            if self.vendedor is None:
                messages.warning(request, "Completa el perfil de tu puesto para gestionar productos.")
                return redirect("usuarios:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Solo los productos del vendedor logueado (evita tocar productos ajenos)."""
        return (
            Producto.objects.filter(vendedor=self.vendedor)
            .prefetch_related("categorias")
            .order_by("nombre")
        )


class MisProductosView(ProductoVendedorMixin, ListView):
    """Pantalla "Mis productos": lista solo los productos del vendedor."""

    model = Producto
    template_name = "productos/mis_productos.html"
    context_object_name = "productos"
    
    
class ProductoCreateView(ProductoVendedorMixin, CreateView):
    """Formulario "Nuevo producto": el producto queda asociado al vendedor logueado."""

    model = Producto
    form_class = ProductoForm
    template_name = "productos/producto_form.html"
    success_url = reverse_lazy("productos:mis_productos")

    def form_valid(self, form):
        form.instance.vendedor = self.vendedor
        messages.success(self.request, "Producto agregado correctamente.")
        return super().form_valid(form)


class ProductoUpdateView(ProductoVendedorMixin, UpdateView):
    """Edita un producto del vendedor logueado."""

    model = Producto
    form_class = ProductoForm
    template_name = "productos/producto_form.html"
    success_url = reverse_lazy("productos:mis_productos")

    def form_valid(self, form):
        messages.success(self.request, "Producto actualizado correctamente.")
        return super().form_valid(form)


class ProductoDeleteView(ProductoVendedorMixin, DeleteView):
    """Pide confirmación y elimina un producto del vendedor logueado."""

    model = Producto
    template_name = "productos/producto_confirm_delete.html"
    success_url = reverse_lazy("productos:mis_productos")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "No puedes eliminar este producto porque tiene pedidos asociados. "
                "Márcalo como no disponible.",
            )
            return redirect("productos:mis_productos")
        messages.success(self.request, "Producto eliminado.")
        return response


class ProductoToggleDisponibleView(ProductoVendedorMixin, View):
    """Alterna un producto entre disponible y no disponible (solo por POST)."""

    def post(self, request, pk):
        producto = get_object_or_404(self.get_queryset(), pk=pk)
        producto.disponible = not producto.disponible
        producto.save(update_fields=["disponible"])
        estado = "disponible" if producto.disponible else "no disponible"
        messages.success(request, f"«{producto.nombre}» ahora está {estado}.")
        return redirect("productos:mis_productos")
    
