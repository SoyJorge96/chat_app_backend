"""Modelos ORM para permisos y su asignación a roles."""

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class PermissionModel(Base):
    """Catálogo de permisos/acciones disponibles en el sistema."""

    __tablename__ = "user_permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    role_permissions = relationship("RolePermissionModel", back_populates="permission")


class RolePermissionModel(Base):
    """Tabla pivote entre roles y permisos."""

    __tablename__ = "user_role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("user_roles.id"),
        index=True,
        nullable=False,
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("user_permissions.id"),
        index=True,
        nullable=False,
    )

    role = relationship("RoleModel", back_populates="role_permissions")
    permission = relationship("PermissionModel", back_populates="role_permissions")
