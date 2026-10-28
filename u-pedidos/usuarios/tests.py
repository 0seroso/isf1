"""Pruebas del panel de ventas."""

from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.test import TestCase
from django.urls import reverse

from pedidos.models import DetallePedido, Pedido
from productos.models import Producto, Vendedor
from usuarios.models import Usuario

SANTIAGO = ZoneInfo("America/Santiago")


class PedidosEntrantesTests(TestCase):
    """Pruebas de la tabla de pedidos entrantes del panel de ventas."""

    @classmethod
    def setUpTestData(cls):
        cls.vendedora = Usuario.objects.create_user(
            username="vendedora_test", password="password123", rol="vendedor"
        )
        cls.comprador = Usuario.objects.create_user(
            username="comprador_test", password="password123", rol="comprador"
        )
        puesto = Vendedor.objects.create(usuario=cls.vendedora, nombre="Puesto Propio")
        otro_puesto = Vendedor.objects.create(nombre="Puesto Ajeno")
        charquican = Producto.objects.create(
            vendedor=puesto, nombre="Charquicán", precio=3500, stock=10
        )
        cazuela = Producto.objects.create(
            vendedor=otro_puesto, nombre="Cazuela", precio=4000, stock=10
        )
        jueves_13_00 = datetime(2026, 10, 8, 13, 0, tzinfo=SANTIAGO)
        viernes_12_00 = datetime(2026, 10, 9, 12, 0, tzinfo=SANTIAGO)
        viernes_12_05 = datetime(2026, 10, 9, 12, 5, tzinfo=SANTIAGO)
        cls.pedido_antiguo = cls.crear_pedido(charquican, 1, jueves_13_00)
        cls.pedido_reciente = cls.crear_pedido(charquican, 2, viernes_12_05)
        cls.crear_pedido(cazuela, 1, viernes_12_00)

    @classmethod
    def crear_pedido(cls, producto: Producto, cantidad: int, fecha: datetime) -> Pedido:
        """Crea un pedido de `cantidad` unidades de `producto`, hecho en `fecha`."""
        pedido = Pedido.objects.create(comprador=cls.comprador, fecha_creacion=fecha)
        DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio,
        )
        return pedido

    def ver_panel(self):
        """Pide el panel de ventas como la vendedora."""
        self.client.force_login(self.vendedora)
        return self.client.get(reverse("usuarios:panel_vendedor"))

    def test_solo_pedidos_del_puesto_mas_recientes_primero(self):
        """La tabla trae solo los pedidos del puesto, del más reciente al más antiguo."""
        entrantes = self.ver_panel().context["pedidos_entrantes"]
        pedidos = [detalle.pedido for detalle in entrantes]
        self.assertEqual(pedidos, [self.pedido_reciente, self.pedido_antiguo])

    def test_columnas_de_la_tabla(self):
        """La tabla muestra ID, producto, comprador, cantidad, monto y fecha/hora."""
        respuesta = self.ver_panel()
        encabezados = ["ID del pedido", "Producto", "Comprador", "Cantidad", "Monto", "Fecha/Hora", "Retiro"]
        for encabezado in encabezados:
            self.assertContains(respuesta, f"<th>{encabezado}</th>", html=True)
        fila = (
            f"<tr><td>#{self.pedido_reciente.id}</td><td>Charquicán</td>"
            "<td>comprador_test</td><td>2</td><td>$7000</td><td>09/10/2026 12:05</td>"
            "<td>Sin horario registrado</td></tr>"
        )
        self.assertContains(respuesta, fila, html=True)

    def test_no_muestra_pedidos_de_otros_puestos(self):
        """Los pedidos de productos de otro puesto no aparecen."""
        self.assertNotContains(self.ver_panel(), "Cazuela")

    def test_horario_se_muestra_en_hora_local(self):
        self.pedido_reciente.retiro_inicio = datetime(2026, 10, 9, 13, 30, tzinfo=SANTIAGO)
        self.pedido_reciente.save(update_fields=["retiro_inicio"])

        respuesta = self.ver_panel()

        self.assertContains(respuesta, "09/10/2026 · 13:30–13:50")

    def test_monto_conserva_centavos_y_precio_de_la_reserva(self):
        detalle = self.pedido_reciente.items.get()
        detalle.precio_unitario = Decimal("3500.25")
        detalle.save(update_fields=["precio_unitario"])
        Producto.objects.filter(pk=detalle.producto_id).update(precio=Decimal("9000.00"))

        respuesta = self.ver_panel()

        self.assertContains(respuesta, "$7000,50")
        self.assertNotContains(respuesta, "$18000")

    def test_usuario_anonimo_debe_iniciar_sesion(self):
        respuesta = self.client.get(reverse("usuarios:panel_vendedor"))

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("usuarios:login"), respuesta.url)

    def test_sin_pedidos(self):
        """Sin pedidos, el panel lo indica en vez de mostrar la tabla."""
        Pedido.objects.all().delete()
        respuesta = self.ver_panel()
        self.assertContains(respuesta, "Aún no tienes pedidos.")
        self.assertNotContains(respuesta, "<table")

    def test_comprador_no_ve_el_panel(self):
        """Quien compra no puede entrar al panel de ventas."""
        self.client.force_login(self.comprador)
        respuesta = self.client.get(reverse("usuarios:panel_vendedor"))
        self.assertRedirects(
            respuesta, reverse("usuarios:dashboard"), fetch_redirect_response=False
        )
