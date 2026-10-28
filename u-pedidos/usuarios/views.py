from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from pedidos.models import DetallePedido

from .forms import PerfilVendedorForm, RegistroForm
from .mixins import CompradorRequiredMixin, VendedorRequiredMixin


class RegistroView(CreateView):
    """Crea la cuenta, inicia sesión y envía al dashboard."""

    form_class = RegistroForm
    template_name = "usuarios/registro.html"
    success_url = reverse_lazy("usuarios:dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Cuenta creada. Te damos la bienvenida a U-Pedidos.")
        return response


@login_required
def dashboard_dispatch(request):
    """Redirige a cada persona a su panel según el rol."""
    user = request.user
    if user.rol == "vendedor":
        if hasattr(user, "vendedor"):
            return redirect("usuarios:panel_vendedor")
        return redirect("usuarios:completar_perfil_vendedor")
    if user.rol == "comprador":
        return redirect("usuarios:panel_comprador")
    logout(request)
    messages.error(
        request,
        "Tu cuenta no tiene rol asignado. Contacta al administrador.",
    )
    return redirect("usuarios:login")


class PanelVendedorView(LoginRequiredMixin, VendedorRequiredMixin, TemplateView):
    """Página de inicio de quien vende, con la tabla de pedidos entrantes."""

    template_name = "usuarios/panel_vendedor.html"

    def get_context_data(self, **kwargs):
        """Agrega las líneas de pedido de los productos del puesto, más recientes primero."""
        context = super().get_context_data(**kwargs)
        context["pedidos_entrantes"] = (
            DetallePedido.objects.filter(producto__vendedor__usuario=self.request.user)
            .select_related("pedido__comprador", "producto")
            .order_by("-pedido__fecha_creacion", "-pedido_id")
        )
        return context


class PanelCompradorView(LoginRequiredMixin, CompradorRequiredMixin, TemplateView):
    """Página de inicio de quien compra."""

    template_name = "usuarios/panel_comprador.html"


class CompletarPerfilVendedorView(LoginRequiredMixin, VendedorRequiredMixin, CreateView):
    """Pide nombre y ubicación del puesto a quien vende y aún no tiene perfil."""

    form_class = PerfilVendedorForm
    template_name = "usuarios/completar_perfil_vendedor.html"
    success_url = reverse_lazy("usuarios:panel_vendedor")

    def dispatch(self, request, *args, **kwargs):
        # Si el perfil ya existe, no se vuelve a pedir.
        if request.user.is_authenticated and hasattr(request.user, "vendedor"):
            return redirect("usuarios:panel_vendedor")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)
