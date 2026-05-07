"""BaseModel compartido para respuestas que contienen fechas.

Este archivo existe para evitar repetir la misma serialización en cada DTO que
expone `datetime`.

Objetivo:
- si un datetime viene timezone-aware (por ejemplo UTC desde PostgreSQL),
  convertirlo a la zona configurada
- quitar el tzinfo al serializar JSON
- evitar respuestas con sufijos como `Z` cuando la API quiere mostrar algo más
  cercano a `datetime.now()`
"""

from datetime import datetime

from pydantic import BaseModel, field_serializer

from app.api.v1.shared.utils.datetime_utils import format_datetime_for_response


class DateTimeResponseModel(BaseModel):
    """Base DTO que normaliza datetimes al serializar JSON."""

    @field_serializer("*", when_used="json", check_fields=False)
    def serialize_datetime_fields(self, value):
        if isinstance(value, datetime):
            return format_datetime_for_response(value)
        return value
