"""Manejadores globales de excepciones.

Aquí traducimos excepciones internas del proyecto a respuestas HTTP.

Beneficio principal:
- los `services` pueden lanzar errores del dominio
- la forma final del JSON de error se decide en un solo sitio

Eso evita tener `try/except` repetidos en todos los routers.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los handlers globales de la aplicación.

    Este patrón deja la app preparada para crecer. Si mañana quieres devolver
    más contexto en los errores (por ejemplo código interno, trace id, etc.),
    podrás hacerlo aquí sin tocar todos los endpoints.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        """Convierte una `AppException` en una respuesta JSON uniforme."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_type": exc.__class__.__name__,
            },
        )
