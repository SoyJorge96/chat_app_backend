"""Repositorio del módulo `auth`.

Esta capa gestiona persistencia específica de autenticación, principalmente
refresh tokens guardados en base de datos.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.modules.auth.models import RefreshToken
from app.core.repositories.base import BaseRepository
from app.api.v1.shared.utils.datetime_utils import current_datetime


class AuthRepository(BaseRepository[RefreshToken]):
    """Repositorio especializado para refresh tokens."""

    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model=RefreshToken)

    def get_refresh_token_by_jti(self, jti: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(RefreshToken.jti == jti)
        return self.db.execute(statement).scalar_one_or_none()

    def create_refresh_token(
        self,
        *,
        user_id: int,
        jti: str,
        token_hash: str,
        expires_at,
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            jti=jti,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        return self.save(refresh_token)

    def revoke_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        refresh_token.is_revoked = True
        refresh_token.revoked_at = current_datetime()
        return self.save(refresh_token)
