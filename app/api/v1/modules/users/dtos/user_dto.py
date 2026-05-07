"""DTOs / Schemas del módulo `users`.

DTO significa Data Transfer Object.
En esta plantilla, estos esquemas cumplen dos papeles principales:

1. Validar lo que entra desde HTTP.
2. Definir la forma exacta de lo que sale hacia el cliente.

Regla importante:
- aquí NO va SQL
- aquí NO va lógica de negocio pesada
- aquí NO va persistencia

Este archivo solo describe y valida datos.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.api.v1.shared.dtos.base_datetime_response import DateTimeResponseModel
from app.api.v1.shared.dtos.pagination_dto import PaginationMeta


class UserCreate(BaseModel):
    """Payload para crear un usuario desde el módulo users.

    Como el modelo ya soporta autenticación, aquí también pedimos contraseña.
    """

    full_name: str = Field(..., min_length=3, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    is_active: bool = True


class UserUpdate(BaseModel):
    """Payload parcial para actualizar un usuario.

    Nota:
    - aquí NO cambiamos contraseña
    - para eso convendría un caso de uso específico de auth
    """

    full_name: str | None = Field(default=None, min_length=3, max_length=120)
    email: EmailStr | None = None
    is_active: bool | None = None


class UserResponse(DateTimeResponseModel):
    """Schema de salida expuesto por la API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Respuesta completa de listado."""

    items: list[UserResponse]
    meta: PaginationMeta
