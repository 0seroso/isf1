from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("registro/", views.RegistroView.as_view(), name="registro"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard_dispatch, name="dashboard"),
    path("panel-vendedor/", views.PanelVendedorView.as_view(), name="panel_vendedor"),
    path("panel-comprador/", views.PanelCompradorView.as_view(), name="panel_comprador"),
    path(
        "completar-perfil-vendedor/",
        views.CompletarPerfilVendedorView.as_view(),
        name="completar_perfil_vendedor",
    ),
]
