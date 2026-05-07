"""Registro central de modelos ORM.

Este archivo importa los modelos de todos los módulos para que SQLAlchemy y
Alembic los detecten.
"""

from app.api.v1.modules.auth.models import RefreshToken  # noqa: F401
from app.api.v1.modules.users.models.user_model import UserModel  # noqa: F401
from app.api.v1.modules.users.models.role_model import RoleModel
from app.api.v1.modules.users.models.permission_model import PermissionModel, RolePermissionModel