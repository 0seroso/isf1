"""Pruebas de la validación de franjas de retiro."""

from datetime import datetime
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from pedidos.franjas import validar_franja_reservable
from pedidos.models import Pedido

SANTIAGO = ZoneInfo("America/Santiago")


def viernes(hora: int, minuto: int) -> datetime:
    """Instante del viernes 9 de octubre de 2026, en hora de Santiago."""
    return datetime(2026, 10, 9, hora, minuto, tzinfo=SANTIAGO)


class ValidarFranjaReservableTests(SimpleTestCase):
    """Pruebas de `validar_franja_reservable`."""

    def assert_rechaza(self, inicio: datetime, ahora: datetime, codigo: str) -> None:
        """Verifica que la franja se rechace con el código indicado."""
        with self.assertRaises(ValidationError) as contexto:
            validar_franja_reservable(inicio, ahora)
        self.assertEqual(contexto.exception.code, codigo)

    def test_franja_futura_de_hoy(self):
        """Una franja de hoy que aún no comienza se puede reservar."""
        validar_franja_reservable(viernes(13, 30), ahora=viernes(12, 0))

    def test_hora_que_no_es_inicio_de_franja(self):
        """Un horario dentro de una franja, pero no en su inicio, se rechaza."""
        self.assert_rechaza(viernes(13, 35), viernes(12, 0), "franja_invalida")

    def test_fuera_de_la_jornada(self):
        """Antes de las 8:30 o desde las 19:30 no hay franjas."""
        self.assert_rechaza(viernes(8, 10), viernes(7, 0), "franja_invalida")
        self.assert_rechaza(viernes(19, 30), viernes(12, 0), "franja_invalida")

    def test_fin_de_semana(self):
        """El sábado no hay franjas, aunque la hora calce con una."""
        sabado = datetime(2026, 10, 10, 13, 30, tzinfo=SANTIAGO)
        self.assert_rechaza(sabado, viernes(12, 0), "franja_invalida")

    def test_otro_dia(self):
        """Solo se reserva para hoy, aunque la franja de otro día sea válida."""
        lunes = datetime(2026, 10, 12, 13, 30, tzinfo=SANTIAGO)
        self.assert_rechaza(lunes, viernes(12, 0), "franja_otro_dia")

    def test_franja_que_esta_comenzando(self):
        """Una franja deja de ser reservable justo cuando comienza."""
        self.assert_rechaza(viernes(13, 30), viernes(13, 30), "franja_comenzada")

    def test_franja_en_curso(self):
        """Una franja en curso no se puede reservar."""
        self.assert_rechaza(viernes(13, 30), viernes(13, 40), "franja_comenzada")


class PedidoCleanTests(SimpleTestCase):
    """Pruebas de `Pedido.clean`."""

    def test_retiro_valido(self):
        """Un pedido con retiro en el inicio de una franja es válido."""
        Pedido(retiro_inicio=viernes(13, 30)).clean()

    def test_retiro_invalido(self):
        """Un retiro fuera de las franjas se informa en el campo retiro_inicio."""
        with self.assertRaises(ValidationError) as contexto:
            Pedido(retiro_inicio=viernes(13, 35)).clean()
        self.assertIn("retiro_inicio", contexto.exception.message_dict)

    def test_retiro_pasado(self):
        """Un pedido antiguo sigue siendo válido aunque su franja ya pasó."""
        Pedido(retiro_inicio=datetime(2026, 1, 5, 13, 30, tzinfo=SANTIAGO)).clean()

    def test_sin_retiro(self):
        """Un pedido sin horario de retiro es válido."""
        Pedido().clean()
