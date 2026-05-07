"""Utilidades de fechas y tiempo.

La idea de tener un módulo así es evitar repetir helpers pequeños en varios
sitios del proyecto.

Antes la plantilla trabajaba en UTC puro y por eso las respuestas salían con
`Z`. Como ahora quieres manejar fechas actuales tipo `datetime.now()`, este
archivo centraliza esa decisión para que toda la app sea coherente.

Además, la API ahora expone fechas en formato legible:

`YYYY-MM-DD HH:MM:SS`
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings

API_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def current_datetime_tz() -> datetime:
    """Devuelve la fecha actual en la zona horaria configurada.

    Este helper devuelve un datetime *aware* (con zona horaria), útil para
    cálculos internos cuando sí necesitamos una referencia horaria completa.
    """
    return datetime.now(ZoneInfo(settings.APP_TIMEZONE))


def current_datetime() -> datetime:
    """Devuelve la fecha actual tipo `datetime.now()`.

    El valor final es *naive* (sin tzinfo) porque el usuario pidió manejar
    fechas como las que normalmente devuelve `datetime.now()`.
    """
    # return current_datetime_tz().replace(tzinfo=None)
    return datetime.now()


def normalize_datetime(value: datetime | None) -> datetime | None:
    """Normaliza cualquier datetime al formato que expone esta API.

    - Si ya viene naive, se deja igual.
    - Si viene timezone-aware (por ejemplo UTC desde la base), se convierte a
      la zona configurada y luego se le quita el tzinfo para que no salga `Z`.
    """
    if value is None:
        return None

    if value.tzinfo is None:
        return value

    return value.astimezone(ZoneInfo(settings.APP_TIMEZONE)).replace(tzinfo=None)


def format_datetime_for_response(value: datetime | None) -> str | None:
    """Formatea un datetime para respuestas JSON de la API.

    Formato final:
    `YYYY-MM-DD HH:MM:SS`

    Ejemplo:
    `2026-05-03 13:40:15`
    """
    normalized_value = normalize_datetime(value)
    if normalized_value is None:
        return None

    return normalized_value.strftime(API_DATETIME_FORMAT)
