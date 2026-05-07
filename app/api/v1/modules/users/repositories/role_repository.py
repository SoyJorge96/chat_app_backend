"""Repositorio del subdominio de roles y permisos.

Aunque el chequeo final de permisos vive en el service, esta capa resuelve
la parte de acceso a datos necesaria para saber:
- si un usuario pertenece a una casa
- con qué rol pertenece
- si la relación ya fue aceptada
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.modules.users.models.permission_model import RolePermissionModel
from app.api.v1.modules.users.models.role_model import RoleModel
from app.core.repositories.base import BaseRepository


class RoleRepository(BaseRepository[RoleModel]):
    """Repositorio para consultas relacionadas con roles dentro de casas."""

    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model=RoleModel)

    
    def get_by_name(self, name:str)-> RoleModel | None:
        query = select(RoleModel).where(RoleModel.name == name)
        return self.db.execute(query).scalar_one_or_none()
