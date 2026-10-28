"""Pruebas del campo de formulario para la franja de retiro."""

from datetime import datetime
from unittest import mock
from zoneinfo import ZoneInfo

from django import forms
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from pedidos.forms import FranjaRetiroField

SANTIAGO = ZoneInfo("America/Santiago")


def viernes(hora: int, minuto: int) -> datetime:
    """Instante del viernes 9 de octubre de 2026, en hora de Santiago."""
    return datetime(2026, 10, 9, hora, minuto, tzinfo=SANTIAGO)


class ReservaDePrueba(forms.Form):
    """Formulario mínimo que usa el campo, como lo haría el de reserva."""

    retiro = FranjaRetiroField()


@mock.patch("django.utils.timezone.now", return_value=viernes(12, 0))
class FranjaRetiroFieldTests(SimpleTestCase):
    """Pruebas de `FranjaRetiroField`, con la hora fijada el viernes a las 12:00."""

    def assert_rechaza(self, valor: str, codigo: str) -> None:
        """Verifica que el campo rechace `valor` con el código indicado."""
        with self.assertRaises(ValidationError) as contexto:
            FranjaRetiroField().clean(valor)
        self.assertEqual(contexto.exception.code, codigo)

    def test_franja_valida(self, _now):
        """Una franja futura de hoy se convierte en su inicio con zona horaria."""
        self.assertEqual(FranjaRetiroField().clean("13:30"), viernes(13, 30))

    def test_formato_invalido(self, _now):
        """Un valor que no es HH:MM se rechaza por formato."""
        self.assert_rechaza("13h30", "invalid")
        self.assert_rechaza("25:00", "invalid")

    def test_hora_que_no_es_inicio_de_franja(self, _now):
        """Un horario que no es inicio de franja se rechaza."""
        self.assert_rechaza("13:35", "franja_invalida")

    def test_franja_comenzada(self, _now):
        """Una franja que ya comenzó se rechaza."""
        self.assert_rechaza("11:50", "franja_comenzada")

    def test_obligatorio(self, _now):
        """Por defecto el campo es obligatorio."""
        self.assert_rechaza("", "required")

    def test_opcional_vacio(self, _now):
        """Si no es obligatorio, un valor vacío queda como None."""
        self.assertIsNone(FranjaRetiroField(required=False).clean(""))

    def test_en_un_formulario(self, _now):
        """En un formulario, la franja limpia queda en cleaned_data."""
        formulario = ReservaDePrueba(data={"retiro": "13:30"})
        self.assertTrue(formulario.is_valid())
        self.assertEqual(formulario.cleaned_data["retiro"], viernes(13, 30))

    def test_error_en_un_formulario(self, _now):
        """En un formulario, el error se asocia al campo de la franja."""
        formulario = ReservaDePrueba(data={"retiro": "11:50"})
        self.assertFalse(formulario.is_valid())
        self.assertIn("retiro", formulario.errors)
