
"""Modelos ORM relacionados con roles."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class RoleModel(Base):
    """Catálogo de roles disponibles dentro de una casa."""

    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)

    house_users = relationship("HouseUserModel", back_populates="role")
    role_permissions = relationship("RolePermissionModel", back_populates="role")
