"""DTOs del módulo `auth`.

Aquí definimos los contratos HTTP específicos de autenticación.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.api.v1.shared.dtos.base_datetime_response import DateTimeResponseModel
from app.api.v1.modules.users.dtos.user_dto import UserResponse


class RegisterRequest(BaseModel):
    """Payload público para registrar un usuario."""

    full_name: str = Field(..., min_length=3, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Payload para autenticarse con email y contraseña."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    """Payload para pedir nuevos tokens a partir de un refresh token."""

    refresh_token: str = Field(..., min_length=20)


class LogoutRequest(BaseModel):
    """Payload para cerrar sesión revocando un refresh token."""

    refresh_token: str = Field(..., min_length=20)


class TokenPairResponse(DateTimeResponseModel):
    """Respuesta estándar de login/register/refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_token_expires_at: datetime
    refresh_token_expires_at: datetime
    user: UserResponse


class AuthenticatedUserResponse(DateTimeResponseModel):
    """Respuesta del endpoint `/auth/me`."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    is_online: bool
    is_superuser: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    """Respuesta simple para operaciones sin payload complejo."""

    message: str
