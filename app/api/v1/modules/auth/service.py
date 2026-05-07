"""Servicio del módulo `auth`.

Aquí vive la lógica de autenticación:
- registro
- login
- refresh
- logout
- usuario actual

Este archivo coordina:
- `UserRepository` para usuarios
- `AuthRepository` para refresh tokens persistidos
- `app.core.security` para hashing y JWT
"""

from app.api.v1.modules.auth.dto import (
    AuthenticatedUserResponse,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenPairResponse,
)
from app.api.v1.modules.auth.repository import AuthRepository
from app.api.v1.shared.utils.datetime_utils import current_datetime, normalize_datetime
from app.api.v1.modules.users.dtos.user_dto import UserResponse
from app.api.v1.modules.users.models.user_model import UserModel
from app.api.v1.modules.users.repositories.user_repository import UserRepository
from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.core.security import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)


class AuthService:
    """Casos de uso del módulo auth."""

    def __init__(self, auth_repository: AuthRepository, user_repository: UserRepository) -> None:
        self.auth_repository = auth_repository
        self.user_repository = user_repository

    def register(self, payload: RegisterRequest) -> UserModel:
        """Registra un usuario y devuelve tokens iniciales."""
        existing_user = self.user_repository.get_by_email(str(payload.email))
        if existing_user is not None:
            raise ConflictError(detail="Ya existe un usuario con ese email")

        user = self.user_repository.create(
            full_name=payload.full_name,
            email=str(payload.email),
            hashed_password=hash_password(payload.password),
            is_active=True,
            is_superuser=False,
        )
        return user

    def login(self, payload: LoginRequest) -> TokenPairResponse:
        """Autentica un usuario con email y contraseña."""
        user = self.user_repository.get_by_email(str(payload.email))
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError(detail="Credenciales inválidas")

        if not user.is_active:
            raise ForbiddenError(detail="El usuario está inactivo")

        user.last_login_at = current_datetime()
        self.user_repository.save(user)

        return self._issue_token_pair(user)

    def refresh_tokens(self, payload: RefreshTokenRequest) -> TokenPairResponse:
        """Entrega un nuevo par de tokens si el refresh token sigue siendo válido."""
        token_payload = self._decode_and_validate_token(payload.refresh_token, expected_type="refresh")

        user_id = self._extract_user_id(token_payload)
        jti = self._extract_jti(token_payload)

        stored_token = self.auth_repository.get_refresh_token_by_jti(jti)
        if stored_token is None:
            raise UnauthorizedError(detail="Refresh token desconocido")

        if stored_token.is_revoked:
            raise UnauthorizedError(detail="Refresh token revocado")

        normalized_expires_at = normalize_datetime(stored_token.expires_at)
        if normalized_expires_at is not None and normalized_expires_at < current_datetime():
            raise UnauthorizedError(detail="Refresh token expirado")

        if stored_token.token_hash != hash_token(payload.refresh_token):
            raise UnauthorizedError(detail="Refresh token inválido")

        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError(detail="Usuario no encontrado para este token")

        if not user.is_active:
            raise ForbiddenError(detail="El usuario está inactivo")

        # Rotación de refresh token: el anterior deja de ser válido.
        self.auth_repository.revoke_refresh_token(stored_token)

        return self._issue_token_pair(user)

    def logout(self, *, current_user: UserModel, refresh_token: str) -> MessageResponse:
        """Revoca el refresh token entregado por el cliente."""
        token_payload = self._decode_and_validate_token(refresh_token, expected_type="refresh")
        user_id = self._extract_user_id(token_payload)
        jti = self._extract_jti(token_payload)

        if user_id != current_user.id:
            raise ForbiddenError(detail="El refresh token no pertenece al usuario autenticado")

        stored_token = self.auth_repository.get_refresh_token_by_jti(jti)
        if stored_token is None:
            raise UnauthorizedError(detail="Refresh token desconocido")

        if stored_token.token_hash != hash_token(refresh_token):
            raise UnauthorizedError(detail="Refresh token inválido")

        if not stored_token.is_revoked:
            self.auth_repository.revoke_refresh_token(stored_token)

        return MessageResponse(message="Sesión cerrada correctamente")

    def get_authenticated_user_response(self, user: UserModel) -> AuthenticatedUserResponse:
        """Convierte la entidad User a la respuesta de `/auth/me`."""
        return AuthenticatedUserResponse.model_validate(user)

    def get_current_user_from_access_token(self, token: str) -> UserModel:
        """Obtiene el usuario actual a partir de un access token."""
        token_payload = self._decode_and_validate_token(token, expected_type="access")
        user_id = self._extract_user_id(token_payload)

        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError(detail="Usuario no encontrado")

        if not user.is_active:
            raise ForbiddenError(detail="El usuario está inactivo")

        return user

    def _issue_token_pair(self, user: UserModel) -> TokenPairResponse:
        """Genera access+refresh token y persiste el refresh token."""
        access_token, _, access_expires_at = create_access_token(subject=str(user.id))
        refresh_token, refresh_jti, refresh_expires_at = create_refresh_token(subject=str(user.id))

        self.auth_repository.create_refresh_token(
            user_id=user.id,
            jti=refresh_jti,
            token_hash=hash_token(refresh_token),
            expires_at=refresh_expires_at,
        )

        return TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_at=access_expires_at,
            refresh_token_expires_at=refresh_expires_at,
            user=UserResponse.model_validate(user),
        )

    def _decode_and_validate_token(self, token: str, *, expected_type: str) -> dict:
        """Decodifica el token y comprueba que sea del tipo esperado."""
        try:
            payload = decode_token(token)
        except TokenError as exc:
            raise UnauthorizedError(detail=str(exc)) from exc

        token_type = payload.get("type")
        if token_type != expected_type:
            raise UnauthorizedError(detail=f"Se esperaba un token de tipo '{expected_type}'")

        return payload

    def _extract_user_id(self, payload: dict) -> int:
        """Extrae el `sub` y lo convierte a int."""
        raw_subject = payload.get("sub")
        if raw_subject is None:
            raise UnauthorizedError(detail="Token sin subject")

        try:
            return int(raw_subject)
        except (TypeError, ValueError) as exc:
            raise UnauthorizedError(detail="Subject de token inválido") from exc

    def _extract_jti(self, payload: dict) -> str:
        """Extrae el identificador único del token."""
        jti = payload.get("jti")
        if not isinstance(jti, str) or not jti:
            raise UnauthorizedError(detail="Token sin jti válido")
        return jti
