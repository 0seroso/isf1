from django.contrib import admin
from productos.models import Categoria, Producto, Vendedor

admin.site.register(Vendedor)
admin.site.register(Categoria)
admin.site.register(Producto)