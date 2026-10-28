"""Pruebas de las franjas que se pueden reservar en un momento dado."""

from datetime import datetime, time
from zoneinfo import ZoneInfo

from django.test import SimpleTestCase

from pedidos.franjas import franjas_reservables

SANTIAGO = ZoneInfo("America/Santiago")


def viernes(hora: int, minuto: int) -> datetime:
    """Instante del viernes 9 de octubre de 2026, en hora de Santiago."""
    return datetime(2026, 10, 9, hora, minuto, tzinfo=SANTIAGO)


class FranjasReservablesTests(SimpleTestCase):
    """Pruebas de `franjas_reservables`."""

    def test_antes_de_la_jornada(self):
        """Antes de las 8:30 se pueden reservar todas las franjas del día."""
        self.assertEqual(len(franjas_reservables(viernes(7, 0))), 33)

    def test_excluye_la_franja_en_curso(self):
        """A las 12:00 la franja 11:50–12:10 ya comenzó; la primera es 12:10."""
        franjas = franjas_reservables(viernes(12, 0))
        self.assertEqual(franjas[0].inicio.time(), time(12, 10))

    def test_excluye_la_franja_que_esta_comenzando(self):
        """A las 13:30 en punto, la franja de las 13:30 ya no se ofrece."""
        franjas = franjas_reservables(viernes(13, 30))
        self.assertEqual(franjas[0].inicio.time(), time(13, 50))

    def test_al_final_del_dia(self):
        """Cuando comenzó la última franja, no queda ninguna."""
        self.assertEqual(franjas_reservables(viernes(19, 15)), [])

    def test_fin_de_semana(self):
        """El sábado no hay franjas que reservar."""
        sabado = datetime(2026, 10, 10, 9, 0, tzinfo=SANTIAGO)
        self.assertEqual(franjas_reservables(sabado), [])

    def test_valor_para_el_formulario(self):
        """El valor de una franja es su inicio en formato HH:MM."""
        self.assertEqual(franjas_reservables(viernes(12, 0))[0].valor, "12:10")
