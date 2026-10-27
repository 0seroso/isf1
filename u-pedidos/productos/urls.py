from django.urls import path

from . import views

app_name = "productos"

urlpatterns = [
    path("", views.CatalogoView.as_view(), name="catalogo"),
    path("mis-productos/", views.MisProductosView.as_view(), name="mis_productos"),
    path("mis-productos/nuevo/", views.ProductoCreateView.as_view(), name="producto_nuevo"),
    path("mis-productos/<int:pk>/editar/", views.ProductoUpdateView.as_view(), name="producto_editar"),
    path("mis-productos/<int:pk>/eliminar/", views.ProductoDeleteView.as_view(), name="producto_eliminar"),
    path("mis-productos/<int:pk>/disponibilidad/", views.ProductoToggleDisponibleView.as_view(), name="producto_disponibilidad"),
]
