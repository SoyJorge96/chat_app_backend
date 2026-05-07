"""Router HTTP del módulo `users`.

Esta es la capa más cercana al protocolo HTTP.

En esta versión de la plantilla, los endpoints de `users` quedan protegidos con
Bearer auth para mostrar cómo aplicar autenticación a otros módulos.
"""

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.modules.auth.dependencies import CurrentUser
from app.api.v1.modules.users.dependencies.user_dependencies import get_user_service
from app.api.v1.modules.users.dtos.user_dto import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.api.v1.modules.users.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=UserListResponse)
def list_users(
    _current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """Lista usuarios.

    `current_user` se inyecta solo para obligar autenticación. En una versión
    más avanzada podrías revisar aquí roles o permisos.
    """
    return service.list_users(page=page, page_size=page_size)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    _current_user: CurrentUser,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Obtiene un usuario por id."""
    return service.get_user(user_id=user_id)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    _current_user: CurrentUser,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Crea un usuario desde el módulo users.

    El registro público normal vive en `/auth/register`.
    Este endpoint puede servir luego para flujos administrativos.
    """
    return service.create_user(payload=payload)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    _current_user: CurrentUser,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Actualiza parcialmente un usuario existente."""
    return service.update_user(user_id=user_id, payload=payload)
