"""Pruebas de los modelos de pedidos."""

from datetime import datetime
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase

from pedidos.models import Pedido

SANTIAGO = ZoneInfo("America/Santiago")


class PedidoRetiroTests(SimpleTestCase):
    """Pruebas del horario de retiro de un pedido."""

    def test_retiro_fin(self):
        """El retiro termina 20 minutos después de su inicio."""
        inicio = datetime(2026, 10, 9, 13, 30, tzinfo=SANTIAGO)
        pedido = Pedido(retiro_inicio=inicio)
        self.assertEqual(pedido.retiro_fin, datetime(2026, 10, 9, 13, 50, tzinfo=SANTIAGO))

    def test_sin_retiro(self):
        """Un pedido sin horario de retiro no tiene fin de retiro."""
        self.assertIsNone(Pedido().retiro_fin)
