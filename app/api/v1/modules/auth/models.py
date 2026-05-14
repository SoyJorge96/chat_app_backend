"""Modelos ORM propios del módulo `auth`.

`User` sigue viviendo en el módulo `users`, porque auth usa al usuario pero no
es dueña del modelo principal.

Aquí sí tiene sentido guardar recursos específicos de autenticación, por
 ejemplo refresh tokens persistidos para permitir revocación/logout real.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.api.v1.shared.utils.datetime_utils import current_datetime
from app.core.db import Base


class RefreshToken(Base):
    """Refresh token persistido.

    Guardamos:
    - `jti`: identificador único del JWT
    - `token_hash`: hash SHA-256 del token real
    - `user_id`: dueño del token
    - `expires_at`: expiración
    - banderas de revocación

    No guardamos el token completo en texto plano para no exponerlo si alguien
    ve la base de datos.
    """

    __tablename__ = "auth_refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("user_users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    jti: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=current_datetime, nullable=False)
