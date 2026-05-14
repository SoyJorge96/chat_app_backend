"""Modelos ORM del módulo `users`.

Aquí se define cómo se representa la tabla en PostgreSQL usando SQLAlchemy.

Regla mental útil:
- `dto.py` describe datos HTTP
- `models.py` describe tablas y columnas reales en la base

Aunque a veces se parecen, no cumplen el mismo propósito.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, Uuid, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api.v1.shared.utils.datetime_utils import current_datetime
from app.core.db import Base


class UserModel(Base):
    """Tabla `users`.

    Este modelo ahora ya está preparado para autenticación basada en email y
    contraseña hasheada.
    """

    __tablename__ = "user_users"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, index=True, nullable=False
    )
    is_online: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )

    # Nunca guardamos la contraseña real. Solo el hash.
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Último login exitoso. Es opcional porque un usuario recién creado aún no
    # necesariamente ha iniciado sesión.
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=current_datetime, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=current_datetime,
        onupdate=current_datetime,
        nullable=False,
    )
