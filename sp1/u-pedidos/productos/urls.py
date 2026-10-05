from django.urls import path
from . import views

app_name = "productos"

urlpatterns = [
    path("", views.CatalogoView.as_view(), name="catalogo"),
]