"""Router HTTP del módulo `auth`.

Aquí exponemos los endpoints públicos y protegidos relacionados con
autenticación.
"""

from fastapi import APIRouter, Depends, status

from app.api.v1.modules.auth.dependencies import CurrentUser, get_auth_service
from app.api.v1.modules.auth.dto import (
    AuthenticatedUserResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenPairResponse,
)
from app.api.v1.modules.auth.service import AuthService
from app.api.v1.modules.users.dtos.user_dto import UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPairResponse:
    """Registra un usuario y devuelve access+refresh tokens."""
    return service.register(payload)


@router.post("/login", response_model=TokenPairResponse)
def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPairResponse:
    """Autentica un usuario usando email y contraseña."""
    return service.login(payload)


@router.post("/refresh", response_model=TokenPairResponse)
def refresh_tokens(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenPairResponse:
    """Entrega un nuevo access token y rota el refresh token."""
    return service.refresh_tokens(payload)


@router.post("/logout", response_model=MessageResponse)
def logout(
    payload: LogoutRequest,
    current_user: CurrentUser,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Cierra sesión revocando el refresh token enviado por el cliente."""
    return service.logout(current_user=current_user, refresh_token=payload.refresh_token)


@router.get("/me", response_model=AuthenticatedUserResponse)
def me(
    current_user: CurrentUser,
    service: AuthService = Depends(get_auth_service),
) -> AuthenticatedUserResponse:
    """Devuelve el usuario autenticado actual."""
    return service.get_authenticated_user_response(current_user)
