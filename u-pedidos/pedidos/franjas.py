"""Franjas de retiro rápido.

La jornada se divide en bloques continuos de 20 minutos, desde el inicio
del primer módulo (8:30) hasta el fin del último (19:30). Con ese origen
todas las franjas parten en :10, :30 o :50, así que 13:30 (fin del módulo
de mediodía) siempre es el inicio de una franja.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

INICIO_JORNADA = time(8, 30)
FIN_JORNADA = time(19, 30)
DURACION_FRANJA = timedelta(minutes=20)
DIAS_HABILES = range(5)  # lunes (0) a viernes (4), según date.weekday()


@dataclass(frozen=True)
class Franja:
    """Bloque de retiro, con inicio y fin en hora local."""

    inicio: datetime
    fin: datetime

    @property
    def etiqueta(self) -> str:
        """Texto para mostrar al usuario, por ejemplo "13:30–13:50"."""
        return f"{self.inicio:%H:%M}–{self.fin:%H:%M}"

    @property
    def valor(self) -> str:
        """Inicio como "HH:MM", el formato que espera FranjaRetiroField."""
        return f"{self.inicio:%H:%M}"


def franjas_del_dia(fecha: date) -> list[Franja]:
    """Franjas de retiro de `fecha`, en hora local; vacía en fin de semana."""
    if fecha.weekday() not in DIAS_HABILES:
        return []

    inicio = datetime.combine(fecha, INICIO_JORNADA)
    fin_jornada = datetime.combine(fecha, FIN_JORNADA)
    franjas = []
    while inicio + DURACION_FRANJA <= fin_jornada:
        fin = inicio + DURACION_FRANJA
        franjas.append(Franja(timezone.make_aware(inicio), timezone.make_aware(fin)))
        inicio = fin
    return franjas


def validar_inicio_de_franja(inicio: datetime) -> None:
    """Lanza ValidationError si `inicio` no es el comienzo de una franja."""
    fecha = timezone.localdate(inicio)
    if not any(franja.inicio == inicio for franja in franjas_del_dia(fecha)):
        raise ValidationError(
            "El horario no corresponde a una franja de retiro.",
            code="franja_invalida",
        )


def validar_franja_reservable(inicio: datetime, ahora: datetime | None = None) -> None:
    """Lanza ValidationError si no se puede reservar la franja que parte en `inicio`.

    Una franja es reservable si es una franja válida, es de hoy y aún no comienza.
    """
    ahora = ahora or timezone.now()
    validar_inicio_de_franja(inicio)
    if timezone.localdate(inicio) != timezone.localdate(ahora):
        raise ValidationError(
            "Solo se puede reservar retiro para hoy.",
            code="franja_otro_dia",
        )
    if inicio <= ahora:
        raise ValidationError(
            "Esa franja de retiro ya comenzó.",
            code="franja_comenzada",
        )


def franjas_reservables(ahora: datetime | None = None) -> list[Franja]:
    """Franjas de hoy que todavía no comienzan, en orden."""
    ahora = ahora or timezone.now()
    franjas = franjas_del_dia(timezone.localdate(ahora))
    return [franja for franja in franjas if franja.inicio > ahora]
