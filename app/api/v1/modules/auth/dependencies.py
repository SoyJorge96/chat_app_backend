"""Dependencias del módulo `auth`.

Aquí se construye la cadena completa para autenticación:

router -> auth service -> repositories -> db session

Además se definen dependencias de seguridad reutilizables como `get_current_user`.
"""

from typing import Annotated, TypeAlias

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.v1.modules.auth.repository import AuthRepository
from app.api.v1.modules.auth.service import AuthService
from app.api.v1.modules.users.models.user_model import UserModel
from app.api.v1.modules.users.repositories.user_repository import UserRepository
from app.core.dependencies import DBSession
from app.core.exceptions import UnauthorizedError

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_repository(db: DBSession) -> AuthRepository:
    """Construye el repositorio específico de auth."""
    return AuthRepository(db)



def get_auth_user_repository(db: DBSession) -> UserRepository:
    """Construye el repositorio de users para que auth lo reutilice."""
    return UserRepository(db)



def get_auth_service(
    auth_repository: AuthRepository = Depends(get_auth_repository),
    user_repository: UserRepository = Depends(get_auth_user_repository),
) -> AuthService:
    """Construye el servicio de autenticación."""
    return AuthService(auth_repository, user_repository)



def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    service: AuthService = Depends(get_auth_service),
) -> UserModel:
    """Obtiene el usuario autenticado a partir del Bearer token."""
    if credentials is None:
        raise UnauthorizedError(detail="Falta el token Bearer")

    return service.get_current_user_from_access_token(credentials.credentials)


CurrentUser: TypeAlias = Annotated[UserModel, Depends(get_current_user)]
