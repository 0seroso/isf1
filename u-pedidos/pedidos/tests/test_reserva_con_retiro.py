"""Pruebas de la reserva con horario de retiro desde el catálogo."""

from datetime import datetime
from unittest import mock
from zoneinfo import ZoneInfo

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from pedidos.models import Pedido
from productos.models import Producto, Vendedor
from usuarios.models import Usuario

SANTIAGO = ZoneInfo("America/Santiago")


def viernes(hora: int, minuto: int) -> datetime:
    """Instante del viernes 9 de octubre de 2026, en hora de Santiago."""
    return datetime(2026, 10, 9, hora, minuto, tzinfo=SANTIAGO)


class ReservaConRetiroTests(TestCase):
    """Pruebas del horario de retiro al reservar, con la hora fijada a las 12:00."""

    @classmethod
    def setUpTestData(cls):
        vendedor = Vendedor.objects.create(nombre="Puesto Test", ubicacion="Patio Central")
        cls.producto = Producto.objects.create(
            vendedor=vendedor, nombre="Charquicán", precio=3500, stock=5
        )
        cls.comprador = Usuario.objects.create_user(
            username="comprador_test", password="password123", rol="comprador"
        )

    def setUp(self):
        self.reloj = mock.patch("django.utils.timezone.now", return_value=viernes(12, 0))
        self.reloj.start()
        self.addCleanup(self.reloj.stop)
        self.client.force_login(self.comprador)

    def reservar(self, **datos):
        """Envía el formulario de reserva de una unidad con los datos indicados."""
        return self.client.post(
            reverse("pedidos:crear_pedido"),
            {"producto_id": self.producto.id, "cantidad": "1", **datos},
        )

    def mensajes(self, respuesta) -> list[str]:
        """Mensajes que la vista dejó para mostrar al usuario."""
        return [m.message for m in get_messages(respuesta.wsgi_request)]

    def assert_no_reserva(self, respuesta, texto: str) -> None:
        """Verifica que no se creó el pedido, no cambió el stock y se avisó `texto`."""
        self.assertRedirects(respuesta, reverse("productos:catalogo"))
        self.assertEqual(Pedido.objects.count(), 0)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 5)
        self.assertTrue(any(texto in m for m in self.mensajes(respuesta)))

    def test_guarda_el_horario_de_retiro(self):
        """El pedido queda con el inicio de la franja elegida."""
        self.reservar(retiro="13:30")
        self.assertEqual(Pedido.objects.get().retiro_inicio, viernes(13, 30))

    def test_confirmacion_muestra_el_horario(self):
        """La confirmación de la reserva indica la franja de retiro."""
        respuesta = self.reservar(retiro="13:30")
        self.assertTrue(any("13:30–13:50" in m for m in self.mensajes(respuesta)))
        catalogo = self.client.get(reverse("productos:catalogo"))
        self.assertContains(catalogo, "Horario de retiro:")
        self.assertContains(catalogo, "13:30–13:50")

    def test_sin_horario_no_reserva(self):
        """Sin horario de retiro no se crea el pedido."""
        self.assert_no_reserva(self.reservar(), "Elige un horario de retiro.")

    def test_franja_comenzada_no_reserva(self):
        """Una franja que ya comenzó no se puede reservar."""
        self.assert_no_reserva(self.reservar(retiro="11:50"), "ya comenzó")

    def test_horario_que_no_es_franja_no_reserva(self):
        """Un horario fuera de las franjas no se puede reservar."""
        self.assert_no_reserva(self.reservar(retiro="13:35"), "no corresponde a una franja")


class SelectorEnCatalogoTests(TestCase):
    """Pruebas del selector de horario en las tarjetas del catálogo."""

    @classmethod
    def setUpTestData(cls):
        vendedor = Vendedor.objects.create(nombre="Puesto Test")
        Producto.objects.create(vendedor=vendedor, nombre="Charquicán", precio=3500, stock=5)
        cls.comprador = Usuario.objects.create_user(
            username="comprador_test", password="password123", rol="comprador"
        )

    def ver_catalogo(self, ahora: datetime):
        """Pide el catálogo como comprador, con la hora fijada en `ahora`."""
        self.client.force_login(self.comprador)
        with mock.patch("django.utils.timezone.now", return_value=ahora):
            return self.client.get(reverse("productos:catalogo"))

    def test_ofrece_solo_franjas_futuras(self):
        """A las 12:00 se ofrece la franja de las 13:30, pero no la de las 11:50."""
        respuesta = self.ver_catalogo(viernes(12, 0))
        self.assertContains(
            respuesta, '<option value="13:30">13:30–13:50</option>', html=True
        )
        self.assertNotContains(respuesta, 'value="11:50"')

    def test_sin_franjas_no_muestra_el_formulario(self):
        """Cuando ya no quedan franjas, se avisa en vez de mostrar el formulario."""
        respuesta = self.ver_catalogo(viernes(19, 15))
        self.assertContains(respuesta, "No quedan horarios de retiro hoy")
        self.assertNotContains(respuesta, reverse("pedidos:crear_pedido"))
