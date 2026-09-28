from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

class RolRequiredMixin(UserPassesTestMixin):
    rol_requerido = None

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.rol == self.rol_requerido

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                "No tienes permiso para acceder a esa página con tu rol actual.",
            )
            return redirect("usuarios:dashboard")
        return super().handle_no_permission()


class VendedorRequiredMixin(RolRequiredMixin):
    rol_requerido = "vendedor"


class CompradorRequiredMixin(RolRequiredMixin):
    rol_requerido = "comprador"
