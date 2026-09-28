from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "email", "rol", "is_staff", "is_active")
    list_filter = ("rol", "is_staff", "is_superuser", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Rol U-Pedidos", {"fields": ("rol",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rol U-Pedidos", {"fields": ("rol",)}),
    )
    search_fields = ("username", "email")
    ordering = ("username",)
