"""Dependencias reutilizables para permisos basados en roles.

La idea es mantener el mismo patrón del proyecto:

dependency -> service -> repository

Así el router solo declara qué permiso necesita y no cómo se resuelve.
"""

from collections.abc import Callable

from fastapi import Depends

from app.api.v1.modules.auth.dependencies import CurrentUser
from app.api.v1.modules.users.repositories.role_repository import RoleRepository
from app.api.v1.modules.users.services.role_service import RoleService
from app.core.dependencies import DBSession


def get_role_repository(db: DBSession) -> RoleRepository:
    """Construye el repositorio de roles/permisos del request actual."""
    return RoleRepository(db)


def get_role_service(
    repository: RoleRepository = Depends(get_role_repository),
) -> RoleService:
    """Construye el service de roles/permisos."""
    return RoleService(repository)
