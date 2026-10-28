"""Pruebas de la generación de franjas de retiro."""

from datetime import date, time, timedelta
from itertools import pairwise

from django.test import SimpleTestCase
from django.utils import timezone

from pedidos.franjas import DURACION_FRANJA, franjas_del_dia

VIERNES = date(2026, 10, 9)
SABADO = date(2026, 10, 10)


class FranjasDelDiaTests(SimpleTestCase):
    """Pruebas de `franjas_del_dia`."""

    def test_dia_habil(self):
        """Un día hábil tiene franjas desde las 8:30 hasta las 19:30."""
        franjas = franjas_del_dia(VIERNES)
        self.assertEqual(len(franjas), 33)
        self.assertEqual(franjas[0].inicio.time(), time(8, 30))
        self.assertEqual(franjas[-1].fin.time(), time(19, 30))

    def test_franjas_continuas(self):
        """Cada franja dura 20 minutos y la siguiente parte cuando termina."""
        franjas = franjas_del_dia(VIERNES)
        for franja in franjas:
            self.assertEqual(franja.fin - franja.inicio, DURACION_FRANJA)
        for anterior, siguiente in pairwise(franjas):
            self.assertEqual(anterior.fin, siguiente.inicio)

    def test_franja_de_las_13_30(self):
        """Siempre hay una franja que parte a las 13:30."""
        inicios = [franja.inicio.time() for franja in franjas_del_dia(VIERNES)]
        self.assertIn(time(13, 30), inicios)

    def test_fin_de_semana(self):
        """Sábado y domingo no hay franjas."""
        self.assertEqual(franjas_del_dia(SABADO), [])
        self.assertEqual(franjas_del_dia(SABADO + timedelta(days=1)), [])

    def test_hora_local(self):
        """Las franjas están en hora de Santiago."""
        franja = franjas_del_dia(VIERNES)[0]
        self.assertTrue(timezone.is_aware(franja.inicio))
        self.assertEqual(str(franja.inicio.tzinfo), "America/Santiago")

    def test_etiqueta(self):
        """La etiqueta muestra inicio y fin en formato HH:MM."""
        self.assertEqual(franjas_del_dia(VIERNES)[0].etiqueta, "08:30–08:50")
