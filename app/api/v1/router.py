"""Router agregador de la versión v1.

Aquí se registran todos los módulos que pertenecen a la versión 1 de la API.
"""

from fastapi import APIRouter

from app.api.v1.modules.auth.router import router as auth_router
from app.api.v1.modules.users.user_router import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
