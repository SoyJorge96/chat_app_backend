"""Excepciones del dominio de la aplicación.

La idea principal aquí es separar:
- reglas de negocio
- detalles HTTP

¿Por qué importa esa separación?
Porque un `service` debería poder decir “esto no existe” o “esto entra en
conflicto” sin tener que saber de FastAPI, `JSONResponse` o status codes.

Entonces el flujo queda así:
1. el service lanza una excepción del dominio
2. el handler global la captura
3. FastAPI responde con un JSON consistente
"""


class AppException(Exception):
    """Excepción base del proyecto."""

    status_code: int = 500
    detail: str = "Ha ocurrido un error inesperado"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class BadRequestError(AppException):
    """Se usa cuando la solicitud es válida a nivel HTTP, pero no a nivel de negocio."""

    status_code = 400
    detail = "Solicitud inválida"


class UnauthorizedError(AppException):
    """Se usa cuando faltan credenciales o son inválidas."""

    status_code = 401
    detail = "No autenticado"


class ForbiddenError(AppException):
    """Se usa cuando el usuario existe, pero no puede ejecutar la acción."""

    status_code = 403
    detail = "No autorizado para realizar esta acción"


class NotFoundError(AppException):
    """Se usa cuando un recurso solicitado no existe."""

    status_code = 404
    detail = "Recurso no encontrado"


class ConflictError(AppException):
    """Se usa cuando una operación choca con el estado actual de los datos."""

    status_code = 409
    detail = "Conflicto de datos"
