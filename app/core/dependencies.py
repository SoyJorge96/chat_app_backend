"""Dependencias compartidas entre módulos.

Aquí viven piezas reutilizables que pueden ser inyectadas con `Depends(...)`.
La idea es no repetir la misma firma en todos los módulos.

Ejemplo actual:
- `DBSession` representa “dame una sesión SQLAlchemy para este request”.

Más adelante aquí podrías agregar:
- usuario autenticado actual
- tenant actual
- permisos comunes
- paginación estándar
"""

from typing import Annotated, TypeAlias

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db_session


# `Annotated[...]` nos permite definir un alias de dependencia reutilizable.
# Así, en vez de escribir esto en cada función:
#
#     db: Session = Depends(get_db_session)
#
# podemos escribir simplemente:
#
#     db: DBSession
#
# Eso hace el código más limpio y consistente.
#
# `TypeAlias` es importante para que analizadores estáticos como Pylance
# entiendan que `DBSession` no es una variable cualquiera, sino un alias de
# tipo válido dentro de anotaciones como:
#
#     def get_user_repository(db: DBSession) -> UserRepository:
#         ...
DBSession: TypeAlias = Annotated[Session, Depends(get_db_session)]
