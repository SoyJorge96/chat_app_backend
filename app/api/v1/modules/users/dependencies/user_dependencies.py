"""Dependencias del módulo `users`.

Este archivo arma la cadena de construcción del módulo:

router -> service -> repository -> db session

Separarlo en un archivo propio ayuda a que el router no tenga que saber
cómo se construye internamente cada pieza.
"""

from fastapi import Depends

from app.api.v1.modules.users.repositories.user_repository import UserRepository
from app.api.v1.modules.users.services.user_service import UserService
from app.core.dependencies import DBSession


def get_user_repository(db: DBSession) -> UserRepository:
    """Construye el repositorio del módulo usando la sesión actual.

    El repositorio es la capa que sí conoce SQLAlchemy y la base de datos.
    """
    return UserRepository(db)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Construye el service del módulo.

    El service depende del repositorio, no del router y no de FastAPI.
    Esta separación ayuda a mantener el dominio limpio y fácil de testear.
    """
    return UserService(repository)
